import importlib
import pkgutil

import httpx
import trio
from holehe.core import get_functions, launch_module


def import_submodules(package, recursive=True):
    """Get all the holehe submodules"""
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        # full_name = package.__name__ + '.' + name
        full_name= name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results

class HoleheAgent:
    @classmethod
    def check_email(cls, email: str):
        return trio.run(cls._do_check, email)

    @staticmethod
    async def _do_check(email: str):
        pkg = importlib.import_module('holehe.modules')
        modules = import_submodules(pkg)
        websites = get_functions(modules)
        client = httpx.AsyncClient()
        # Launching the modules
        out = []
        async with trio.open_nursery() as nursery:
            for website in websites:
                nursery.start_soon(launch_module, website, email, client, out)

        # Sort by modules names
        out = sorted(out, key=lambda i: i['name'])
        # Close the client
        await client.aclose()
        return out
