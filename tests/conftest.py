"""Общие вспомогательные утилиты для тестов."""

from twisted.internet import defer


def resolved(value: object) -> defer.Deferred:
    """Вернуть уже завершённый Deferred.

    Удобно для мокирования асинхронных репозиториев.
    """
    d: defer.Deferred = defer.Deferred()
    d.callback(value)
    return d
