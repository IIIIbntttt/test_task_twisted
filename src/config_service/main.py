import os

from twisted.internet import defer, reactor
from twisted.web.server import Site

from config_service import container
from config_service.infrastructure.database.connection import create_connection_pool
from config_service.infrastructure.database.migrations import run_migrations


@defer.inlineCallbacks
def _setup() -> defer.Deferred:
    pool = create_connection_pool()
    yield run_migrations(pool)

    app = container.build(pool)

    port = int(os.environ.get("PORT", "8080"))
    reactor.listenTCP(port, Site(app.resource()))  # type: ignore[attr-defined]
    print(f"Config service started on port {port}")


def main() -> None:
    def on_error(failure: object) -> None:
        print(f"Startup error: {failure}")
        reactor.stop()  # type: ignore[attr-defined]

    reactor.callWhenRunning(lambda: _setup().addErrback(on_error))  # type: ignore[attr-defined]
    reactor.run()  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
