import imghdr
import aiohttp
from PIL import Image
import aiofiles
import asyncio
import os


async def download_site(session, url, save_name):
    async with session.get(url) as response:
        if response.status == 200:
            try:
                save_path = save_name
                file = await aiofiles.open(save_path, mode='wb')
                await file.write(await response.read())
                await file.close()
                file_extension = imghdr.what(save_path)
                if file_extension is not None:
                    new_name = save_path[:save_path.rindex(".")]
                    os.rename(save_path, new_name)
                    im = Image.open(new_name).convert("RGB")
                    os.remove(new_name)
                    im.save(save_path)
            except Exception as e:
                print(e)


async def download_all_sites(sites, img_save_name):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index in range(len(sites)):
            url = sites[index]
            save_name = img_save_name[index]
            task = asyncio.ensure_future(download_site(session, url, save_name))
            tasks.append(task)
            await asyncio.gather(*task, return_exceptions=True)


def download_img(img_path_list, img_save_list):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download_all_sites(img_path_list, img_save_list))
    mapping = list(zip(img_path_list, img_save_list))
    return mapping
