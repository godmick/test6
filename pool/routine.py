"""Functions to manage pooling."""

import argparse
import asyncio
from typing import Dict, List, Set, Union, cast

from graphzer.entities.io import Results
from graphzer.entities.tasks import TasksList
from graphzer.io.printers import display_results
from graphzer.io.readers import read_domains
from graphzer.io.writers import write_results
from graphzer.pool.domain import Domain, Url
from graphzer.pool.tasks import consume_tasks, init_domain_tasks
from graphzer.utils.filters import filter_urls
from graphzer.utils.logger import get_logger
from graphzer.utils.webhook import send_webhook


async def domain_routine(
    domain: Domain,
    args: argparse.Namespace,
) -> Dict[str, Union[str, Set[Url]]]:
    """Start domain routine."""

    _tasks: TasksList = init_domain_tasks(domain, args)
    _urls: Set[Url] = await consume_tasks(_tasks, domain)

    return {'domain': domain.url, 'urls': filter_urls(_urls)}


async def main_routine(args: argparse.Namespace) -> Results:
    """Main pool routine."""

    logger = get_logger()
    logger.info('starting main routine..')

    # Read domains from either single domain argument or file
    domains: List[Domain] = read_domains(
        file=getattr(args, 'input_file', None),
        domain=getattr(args, 'domain', None),
        precision_mode=args.precision_mode
    )

    if not domains:
        logger.error('no valid domains found to scan')
        return {}

    logger.info(f'scanning {len(domains)} domain(s)')

    # Store output file reference and remove from args to avoid conflicts
    output_file = args.output_file
    del args.output_file

    # Process all domains and collect results
    results: Results = {}
    
    # Process domains sequentially to avoid overwhelming target servers
    for domain in domains:
        logger.info(f'running scan on {domain.url}')
        try:
            result = await domain_routine(domain, args)
            domain_name = cast(str, result['domain'])
            domain_urls = cast(Set[Url], result['urls'])
            results[domain_name] = domain_urls
        except Exception as e:
            logger.error(f'error scanning domain {domain.url}: {e}')
            results[domain.url] = set()

    # Display results
    if not args.quiet_mode:
        # Determine if this is bulk mode (file input) or single domain mode
        is_bulk_mode = getattr(args, 'input_file', None) is not None
        display_results(results, bulk_mode=is_bulk_mode)

    # Write results to file if specified
    if output_file is not None:
        write_results(output_file, results.copy())

    # Send webhook if specified
    if args.webhook_url is not None:
        send_webhook(args.webhook_url, results)

    return results
