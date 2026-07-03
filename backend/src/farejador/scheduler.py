"""
Scheduler do Farejador — dispara o worker periodicamente via APScheduler.
"""
import asyncio
import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger



logger = logging.getLogger(__name__)
_scheduler: Optional[AsyncIOScheduler] = None


def _job_wrapper() -> None:
    """Wrapper do job para rodar no scheduler."""
    # Import lazy para evitar ciclo com __init__.py
    from src.farejador.worker import executar_farejador
    try:
        resultado = asyncio.run(executar_farejador())
        logger.info(
            "🕵️  Farejador executado: %d faros criados",
            resultado["faros_criados"]["total"],
        )
    except Exception as e:
        logger.exception("Erro no job do farejador: %s", e)


def iniciar_scheduler(
    cron_expression: str = "0 */6 * * *",
    timezone: str = "America/Sao_Paulo",
) -> AsyncIOScheduler:
    """Inicia o scheduler em background."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler

    _scheduler = AsyncIOScheduler(timezone=timezone)

    try:
        minute, hour, day, month, day_of_week = cron_expression.split()
        trigger = CronTrigger(
            minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week,
            timezone=timezone,
        )
    except (ValueError, AttributeError):
        trigger = IntervalTrigger(hours=6, timezone=timezone)

    _scheduler.add_job(
        _job_wrapper,
        trigger=trigger,
        id="farejador_main",
        name="Execução principal do Farejador",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.add_job(
        _job_wrapper,
        trigger=IntervalTrigger(minutes=30, timezone=timezone),
        id="farejador_healthcheck",
        name="Verificação periódica",
        replace_existing=True,
        max_instances=1,
    )

    _scheduler.start()
    logger.info("🕵️  Scheduler do Farejador iniciado (cron: %s, tz: %s)", cron_expression, timezone)
    return _scheduler


def parar_scheduler() -> None:
    """Para o scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("🕵️  Scheduler do Farejador parado")


def status_scheduler() -> dict:
    """Retorna o status do scheduler e dos jobs."""
    if not _scheduler:
        return {"running": False, "jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {"running": _scheduler.running, "jobs": jobs}


if __name__ == "__main__":
    import os
    import signal
    import sys
    import time

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    sched = iniciar_scheduler()

    def _shutdown(signum, frame):
        logger.info("Recebido sinal %s, parando scheduler...", signum)
        parar_scheduler()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    logger.info("⏳ Scheduler rodando, aguardando jobs... (PID %d)", os.getpid())

    # Mantém o processo vivo
    while True:
        time.sleep(60)
