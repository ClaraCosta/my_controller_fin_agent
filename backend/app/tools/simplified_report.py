from sqlalchemy.orm import Session


class SimplifiedReportTool:
    def __init__(self, db: Session | None = None):
        self.db = db

    def run(self, message: str, search_results: dict) -> dict:
        data_points = []
        lower_message = message.lower()
        aggregates = search_results.get("aggregates", {})

        if search_results["clients"]:
            data_points.append(f"{len(search_results['clients'])} cliente(s) relacionado(s) encontrados")
        if search_results.get("contacts"):
            data_points.append(f"{len(search_results['contacts'])} contato(s) relacionado(s) encontrados")
        if search_results.get("documents"):
            data_points.append(f"{len(search_results['documents'])} documento(s) relacionado(s) encontrados")
        if search_results["requests"]:
            data_points.append(f"{len(search_results['requests'])} solicitação(ões) relacionada(s) encontradas")
        if not data_points:
            data_points.append("Nenhum registro correspondente foi encontrado na base local")

        shortcut_summary = self._build_shortcut_summary(lower_message, search_results, data_points)
        aggregate_summary = self._build_aggregate_summary(lower_message, search_results, aggregates)
        if shortcut_summary:
            summary = shortcut_summary
        elif aggregate_summary:
            summary = aggregate_summary
        elif "criar cliente" in lower_message or "novo cliente" in lower_message:
            if search_results["clients"]:
                first_client = search_results["clients"][0]["name"]
                summary = (
                    f"Encontrei cliente(s) relacionado(s) ao pedido. O mais próximo foi '{first_client}'. "
                    "Se a intenção for cadastrar um novo cliente, siga com a criação apenas se ele realmente ainda não existir na base."
                )
            else:
                summary = (
                    "Não encontrei cliente correspondente na base atual. "
                    "Você pode seguir com o cadastro de um novo cliente usando o fluxo de criação disponível na dashboard."
                )
        elif "localizar" in lower_message or "buscar" in lower_message or "encontrar" in lower_message:
            summary = (
                f"Consulta operacional para: '{message}'. "
                f"Resultado resumido: {'; '.join(data_points)}."
            )
        else:
            summary = (
                f"{'; '.join(data_points)}."
            )

        return {"summary": summary, "data_points": data_points, "source": "system_data"}

    def _build_aggregate_summary(self, lower_message: str, search_results: dict, aggregates: dict) -> str | None:
        if self._asks_about_receipts(lower_message):
            total = aggregates.get("total_receipts", 0)
            pending = aggregates.get("total_pending_documents", 0)
            processed = aggregates.get("total_processed_documents", 0)
            return (
                f"No momento, identifiquei {total} recibo(s) cadastrados no sistema. "
                f"Entre os documentos consolidados, há {processed} processado(s) e {pending} pendente(s) para revisão humana."
            )

        if self._asks_about_invoices(lower_message):
            total = aggregates.get("total_invoices", 0)
            pending = aggregates.get("total_pending_documents", 0)
            processed = aggregates.get("total_processed_documents", 0)
            return (
                f"No momento, identifiquei {total} nota(s) fiscal(is) cadastrada(s) no sistema. "
                f"Entre os documentos consolidados, há {processed} processado(s) e {pending} pendente(s) para revisão humana."
            )

        if self._asks_about_documents(lower_message):
            total = aggregates.get("total_documents", 0)
            pending = aggregates.get("total_pending_documents", 0)
            processed = aggregates.get("total_processed_documents", 0)
            if "cliente" in lower_message and search_results.get("documents"):
                client_name = search_results["documents"][0].get("client_name") or "o cliente em contexto"
                client_document_count = len(
                    [
                        item
                        for item in search_results["documents"]
                        if item.get("client_name") == client_name
                    ]
                )
                return (
                    f"Para {client_name}, encontrei {client_document_count} documento(s) sintetizado(s) nesta consulta. "
                    f"No panorama geral da Central Fiscal, existem {total} documento(s), sendo {processed} processado(s) e {pending} pendente(s)."
                )
            return (
                f"No momento, a Central Fiscal possui {total} documento(s) registrados. "
                f"Desse total, {processed} está(ão) processado(s) e {pending} permanece(m) pendente(s)."
            )

        if self._asks_about_contacts(lower_message):
            total = aggregates.get("total_contacts", 0)
            sample_names = ", ".join(item["name"] for item in search_results.get("contacts", [])[:3])
            sample_suffix = f" Alguns contatos sintetizados são: {sample_names}." if sample_names else ""
            return (
                f"No momento, a base possui {total} contato(s) cadastrados. "
                "Considerei os campos operacionais principais, como nome, papel, email e telefone."
                f"{sample_suffix}"
            )

        if self._asks_about_requests(lower_message):
            total = aggregates.get("total_requests", 0)
            return (
                f"No momento, a operação possui {total} solicitação(ões) cadastrada(s). "
                "Se quiser, eu posso detalhar prioridades, status ou clientes relacionados."
            )

        if self._asks_about_clients(lower_message):
            total = aggregates.get("total_clients", 0)
            sample_names = ", ".join(item["name"] for item in search_results.get("clients", [])[:3])
            sample_suffix = f" Alguns registros sintetizados são: {sample_names}." if sample_names else ""
            return (
                f"No momento, a base possui {total} cliente(s) cadastrados. "
                "Essa leitura considera os dados principais de cliente, como nome, CNPJ, status e contato principal."
                f"{sample_suffix}"
            )

        return None

    def _build_shortcut_summary(self, lower_message: str, search_results: dict, data_points: list[str]) -> str | None:
        if "pendencias operacionais" in lower_message or "pendencias" in lower_message:
            return (
                "Claro. Fiz uma leitura inicial das pendências operacionais disponíveis no sistema. "
                f"Resumo encontrado: {'; '.join(data_points)}. "
                "Se quiser, eu também posso organizar isso em formato de relatório para facilitar sua análise."
            )

        if "localizar ou criar um cliente" in lower_message or "criar cliente" in lower_message:
            if search_results["clients"]:
                client_names = ", ".join(item["name"] for item in search_results["clients"][:3])
                return (
                    "Perfeito. Consultei a base para verificar possíveis clientes relacionados ao seu pedido. "
                    f"Encontrei estes nomes mais próximos: {client_names}. "
                    "Se a sua intenção for cadastrar um novo cliente, vale confirmar primeiro se ele já não existe na base. "
                    "Se quiser, eu também posso preparar um relatório com esse resumo."
                )
            return (
                "Perfeito. Consultei a base e não encontrei clientes relacionados ao que você informou até agora. "
                "Nesse cenário, o próximo passo pode ser seguir com o cadastro de um novo cliente no sistema. "
                "Se quiser, eu também posso preparar um relatório com esse resumo."
            )

        if "abrir uma nova solicitacao" in lower_message or "nova solicitacao" in lower_message or "criar solicitacao" in lower_message:
            return (
                "Sem problema. Fiz uma leitura inicial do contexto operacional para apoiar a abertura de uma nova solicitação. "
                f"Resumo disponível no momento: {'; '.join(data_points)}. "
                "Se você quiser, eu posso transformar isso em um relatório resumido antes de seguir."
            )

        if "relatorio rapido" in lower_message or "gere um relatorio rapido" in lower_message:
            return (
                "Claro. Levantei um resumo inicial com base nos dados atualmente encontrados no sistema. "
                f"Panorama consolidado: {'; '.join(data_points)}. "
                "Se quiser, eu posso seguir e estruturar um relatório com essas informações."
            )

        return None

    @staticmethod
    def _asks_about_clients(message: str) -> bool:
        return "cliente" in message and any(term in message for term in ("quant", "qtd", "total", "sobre", "me fale", "mostrar", "mostre"))

    @staticmethod
    def _asks_about_contacts(message: str) -> bool:
        return "contato" in message and any(term in message for term in ("quant", "qtd", "total", "sobre", "me fale", "mostrar", "mostre"))

    @staticmethod
    def _asks_about_documents(message: str) -> bool:
        return "documento" in message and any(term in message for term in ("quant", "qtd", "total", "sobre", "mostrar", "mostre"))

    @staticmethod
    def _asks_about_invoices(message: str) -> bool:
        return ("nota fiscal" in message or "notas fiscais" in message or "nota" in message) and any(
            term in message for term in ("quant", "qtd", "total", "sobre", "mostrar", "mostre")
        )

    @staticmethod
    def _asks_about_receipts(message: str) -> bool:
        return "recibo" in message and any(term in message for term in ("quant", "qtd", "total", "sobre", "mostrar", "mostre"))

    @staticmethod
    def _asks_about_requests(message: str) -> bool:
        return ("solicit" in message or "demanda" in message or "atendimento" in message) and any(
            term in message for term in ("quant", "qtd", "total", "sobre", "mostrar", "mostre")
        )
