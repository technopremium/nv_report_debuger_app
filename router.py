import asyncio
import platform

async def ping(host, count):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, str(count), host]

    process = await asyncio.create_subprocess_exec(*command)
    await process.wait()

async def main():
    host = "192.168.1.1"  # Replace this with your router's IP address
    ping_count = 1         # Set the number of pings you'd like to send per task
    concurrent_pings = 1000  # Set the number of concurrent tasks you'd like to run

    tasks = [asyncio.ensure_future(ping(host, ping_count)) for _ in range(concurrent_pings)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
