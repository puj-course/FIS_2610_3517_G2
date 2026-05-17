from app.models.match import Match


STATUS_LABELS = {
    "upcoming": "Proximo",
    "live": "EN VIVO",
    "finished": "Finalizado",
    "cancelled": "Cancelado",
}


def _ranking_str(ranking) -> str:
    return f"#{ranking}" if ranking else "S/R"


def format_match_summary(match: Match) -> str:
    status_label = STATUS_LABELS.get(match.status.value, match.status.value)
    date_str = match.date.strftime("%Y-%m-%d %H:%M")
    home = match.player_home
    away = match.player_away

    lines = [
        f"<b>{home.name}</b> vs <b>{away.name}</b>",
        f"{match.tournament.name} | {status_label}",
        f"{date_str}",
    ]
    if match.score:
        lines.append(f"Score: {match.score}")
    return "\n".join(lines)


def format_match_detail(match: Match) -> str:
    status_label = STATUS_LABELS.get(match.status.value, match.status.value)
    date_str = match.date.strftime("%Y-%m-%d %H:%M")
    home = match.player_home
    away = match.player_away
    t = match.tournament

    lines = [
        f"<b>Partido:</b> <code>{match.id}</code>",
        "",
        f"<b>{home.name}</b> ({home.country}, {_ranking_str(home.ranking)})",
        "  vs",
        f"<b>{away.name}</b> ({away.country}, {_ranking_str(away.ranking)})",
        "",
        f"<b>Torneo:</b> {t.name}",
        f"<b>Superficie:</b> {t.surface.value} | {t.category}",
        f"<b>Ubicacion:</b> {t.location}",
        "",
        f"<b>Fecha:</b> {date_str}",
        f"<b>Estado:</b> {status_label}",
    ]
    if match.score:
        lines.append(f"<b>Score:</b> {match.score}")
    return "\n".join(lines)


def format_match_list(matches: list[Match], total: int) -> str:
    if not matches:
        return "No se encontraron partidos."

    parts = []
    for i, match in enumerate(matches, 1):
        parts.append(f"<b>{i}.</b> {format_match_summary(match)}")

    header = f"<b>Partidos de tenis:</b> {total} encontrado(s)\n"
    result = header + "\n\n".join(parts)

    if total > len(matches):
        result += f"\n\n<i>Mostrando {len(matches)} de {total}.</i>"
    return result


def format_health(status: str, version: str, data_mode: str) -> str:
    return (
        "<b>OddsEngine Status</b>\n"
        f"Estado: {status}\n"
        f"Version: {version}\n"
        f"Modo de datos: {data_mode}"
    )
