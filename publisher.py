from datetime import datetime, timedelta
import os
from random import randint

from modules.VK_poster import PostFactory
from config import update_start_time

from vk_api.exceptions import ApiError

def publisher_image(TOKEN: str, GROUPS_DATA: dict):
    post_factory = PostFactory(token=TOKEN)

    for group_id in GROUPS_DATA.keys():
        start_date = datetime.strptime(GROUPS_DATA[group_id]['start_from'], "%d.%m.%Y")

        if not os.path.exists(f"./images/{group_id}"):
            os.makedirs(f"./images/{group_id}")

        image_files = [f for f in os.listdir(f"./images/{group_id}") if f.endswith(('.jpg', '.png', '.jpeg', '.bmp'))]
        while (len(image_files) > 0):
            index = randint(0, len(image_files) - 1)
            image_name = image_files[index]
            image_path = os.path.join(f"./images/{group_id}", image_name)

            post = post_factory.create_post(
                int(group_id),
                "",
                [
                    image_path
                ]
            )
            
            post.set_publish_date(start_date)
            while (True):
                try:
                    post.publish()
                    break
                except ApiError:
                    start_date += timedelta(minutes=1)
                    post.set_publish_date(start_date)
            
            print(image_name)
            os.remove(image_path)
            image_files.pop(index)
            start_date += timedelta(hours=3)
            update_start_time(group_id, start_date)

            # print(group_id, promts, start_date)