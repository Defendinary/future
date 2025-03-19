import sched
import time

# Set up a scheduler (like cron or APScheduler) to run these checks periodically.

scheduler = sched.scheduler(time.time, time.sleep)

def periodic_check(scheduler, interval, action, *args):
    action(*args)  # Run the action with arguments
    scheduler.enter(interval, 1, periodic_check, (scheduler, interval, action) + args)

# Start the checks
scheduler.enter(0, 1, periodic_check, (scheduler, 60, check_dns, 'example.com'))
scheduler.enter(0, 1, periodic_check, (scheduler, 60, check_ssh_banner, 'example.com'))

# Run the scheduler
scheduler.run()


# ---

import threading

def periodic_check(interval, action, *args):
    action(*args)  # Execute the check
    threading.Timer(interval, periodic_check, [interval, action] + list(args)).start()

# Run the checks every 60 seconds
periodic_check(60, check_dns, 'example.com')
periodic_check(60, check_ssh_banner, 'example.com')


# ---


import asyncio

async def periodic_check(interval, action, *args):
    while True:
        await action(*args)
        await asyncio.sleep(interval)

# Define asynchronous DNS and SSH functions for asyncio
async def check_dns_async(domain):
    check_dns(domain)  # Call synchronous function
    await asyncio.sleep(0)

async def check_ssh_banner_async(host):
    check_ssh_banner(host)
    await asyncio.sleep(0)

# Run tasks
asyncio.run(asyncio.gather(
    periodic_check(60, check_dns_async, 'example.com'),
    periodic_check(60, check_ssh_banner_async, 'example.com')
))



