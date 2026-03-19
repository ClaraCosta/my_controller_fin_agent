import json

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.core.config import settings
from backend.app.services.ollama_service import OllamaService
from backend.app.tools.record_search import RecordSearchTool
from backend.app.tools.simplified_report import SimplifiedReportTool


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.search_tool = RecordSearchTool(db)
        self.report_tool = SimplifiedReportTool(db)
        self.ollama_service = OllamaService()

    def handle_message(self, user: User, payload):
        session = self.chat_repository.get_or_create_session(user_id=user.id, session_id=payload.session_id)
        self.chat_repository.add_message(session.id, "user", payload.message)

        recent_messages = self.chat_repository.list_recent_messages(session.id, limit=8)
        search_results = self.search_tool.run(payload.message)
        fallback_answer = self.report_tool.run(payload.message, search_results)
        llm_summary = ""
        if not self._should_bypass_llm(payload.message):
            llm_summary = self._generate_llm_answer(
                message=payload.message,
                recent_messages=recent_messages,
                search_results=search_results,
                fallback_answer=fallback_answer,
            )
        answer = {
            **fallback_answer,
            "summary": llm_summary or fallback_answer["summary"],
            "source": "ollama" if llm_summary else fallback_answer["source"],
        }

        self.chat_repository.add_message(session.id, "assistant", answer["summary"], metadata_json=json.dumps(answer))
        self.db.commit()
        return {"session_id": session.id, "answer": answer}

    def get_current_session_state(self, user: User) -> dict:
        session = self.chat_repository.get_latest_session(user.id)
        if not session:
            return {"session_id": None, "messages": []}

        messages = self.chat_repository.list_messages(session.id)
        return {
            "session_id": session.id,
            "messages": [{"role": item.role, "content": item.content} for item in messages],
        }

    def _generate_llm_answer(self, message: str, recent_messages: list, search_results: dict, fallback_answer: dict) -> str:
        prompt = self._build_chat_prompt(
            message=message,
            recent_messages=recent_messages,
            search_results=search_results,
            fallback_answer=fallback_answer,
        )
        return self.ollama_service.generate(prompt)

    @staticmethod
    def _should_bypass_llm(message: str) -> bool:
        lower_message = message.lower()
        generic_intents = ("quant", "qtd", "total", "sobre", "mostrar", "mostre", "me fale")
        entities = (
            "cliente",
            "clientes",
            "contato",
            "contatos",
            "documento",
            "documentos",
            "recibo",
            "recibos",
            "nota fiscal",
            "notas fiscais",
            "nota",
            "notas",
            "solicitacao",
            "solicitação",
            "solicitacoes",
            "solicitações",
            "demanda",
            "demandas",
            "atendimento",
            "atendimentos",
            "ocr",
            "central fiscal",
        )

        if any(term in lower_message for term in ("pendencias operacionais", "localizar ou criar um cliente", "criar cliente", "criar solicitacao", "criar solicitação", "nova solicitacao", "nova solicitação", "relatorio rapido")):
            return True

        return any(intent in lower_message for intent in generic_intents) and any(entity in lower_message for entity in entities)

    def _build_chat_prompt(self, message: str, recent_messages: list, search_results: dict, fallback_answer: dict) -> str:
        aggregates = search_results.get("aggregates", {})
        conversation_context = "\n".join(
            f"- {item.role}: {item.content}"
            for item in recent_messages[-6:]
        ) or "- Nenhuma mensagem anterior relevante."

        clients_context = "\n".join(
            f"- Cliente #{item['id']}: {item['name']} (status: {item['status']})"
            for item in search_results.get("clients", [])
        ) or "- Nenhum cliente encontrado."

        contacts_context = "\n".join(
            f"- Contato #{item['id']}: {item['name']} | papel: {item['role']} | email: {item['email']} | telefone: {item['phone']}"
            for item in search_results.get("contacts", [])
        ) or "- Nenhum contato encontrado."

        requests_context = "\n".join(
            f"- Solicitação #{item['id']}: {item['title']} (prioridade: {item['priority']}, status: {item['status']})"
            for item in search_results.get("requests", [])
        ) or "- Nenhuma solicitação encontrada."

        documents_context = "\n".join(
            f"- Documento #{item['id']}: {item['type']} | cliente: {item['client_name']} | status: {item['status']} | entrada: {item['entry_mode']}"
            for item in search_results.get("documents", [])
        ) or "- Nenhum documento encontrado."

        aggregates_context = f"""
- total_clients: {aggregates.get("total_clients", 0)}
- total_contacts: {aggregates.get("total_contacts", 0)}
- total_documents: {aggregates.get("total_documents", 0)}
- total_requests: {aggregates.get("total_requests", 0)}
- total_receipts: {aggregates.get("total_receipts", 0)}
- total_invoices: {aggregates.get("total_invoices", 0)}
- total_pending_documents: {aggregates.get("total_pending_documents", 0)}
- total_processed_documents: {aggregates.get("total_processed_documents", 0)}
""".strip()

        return f"""
Você é o chat central operacional da plataforma {settings.app_name}.
Seu papel é responder com base apenas nos dados do sistema fornecidos abaixo.

Regras obrigatórias:
- não invente informações
- não afirme existência de registros que não estejam no contexto
- se faltar dado, diga claramente que não encontrou ou que precisa de confirmação humana
- responda em português do Brasil
- seja objetivo, útil e operacional
- quando a intenção parecer de cadastro, oriente o próximo passo sem dizer que já criou algo
- se a pergunta for sobre clientes, use primeiro os dados agregados de clientes e depois os exemplos sintetizados da tabela de clientes
- se a pergunta for sobre contatos, use primeiro os dados agregados de contatos e depois os exemplos sintetizados da tabela de contatos
- se a pergunta for sobre solicitações, use primeiro os dados agregados de solicitações e depois os registros sintetizados encontrados
- se a pergunta for sobre notas fiscais, recibos ou documentos, use primeiro os dados agregados da Central Fiscal e depois os registros sintetizados encontrados
- para clientes, considere como campos principais: nome, CNPJ, status e contato principal
- para contatos, considere como campos principais: nome, papel, email e telefone
- para documentos, considere como campos principais: tipo, status, modo de entrada e cliente relacionado
- para solicitações, considere como campos principais: título, prioridade e status
- se o usuário fizer uma pergunta genérica como "quantos clientes existem?" ou "me fale sobre os recibos", responda com os totais e um pequeno resumo dos registros sintetizados
- se a intenção parecer de consulta, responda com base nos dados encontrados, mesmo que seja para dizer que não encontrou algo
- se o cliente chegar falando somente um cumprimento simples como "oi", "olá", "bom dia", "boa tarde", "boa noite", responda de forma simpática e convide-o a pedir informações, buscas ou relatórios

Mensagem atual do usuário:
{message}

Histórico recente da conversa:
{conversation_context}

Clientes encontrados:
{clients_context}

Contatos encontrados:
{contacts_context}

Solicitações encontradas:
{requests_context}

Documentos encontrados:
{documents_context}

Dados agregados do sistema:
{aggregates_context}

Resumo operacional de fallback:
{fallback_answer["summary"]}

Responda em no máximo 4 frases curtas, sem markdown.
""".strip()
