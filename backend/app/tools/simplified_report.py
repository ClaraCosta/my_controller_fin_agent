class SimplifiedReportTool:
    def run(self, message: str, search_results: dict) -> dict:
        data_points = []
        if search_results["clients"]:
            data_points.append(f"{len(search_results['clients'])} cliente(s) relacionado(s) encontrados")
        if search_results["requests"]:
            data_points.append(f"{len(search_results['requests'])} solicitação(ões) relacionada(s) encontradas")
        if not data_points:
            data_points.append("Nenhum registro correspondente foi encontrado na base local")

        summary = (
            f"Consulta operacional para: '{message}'. "
            f"Resultado resumido: {'; '.join(data_points)}."
        )
        return {"summary": summary, "data_points": data_points, "source": "system_data"}

