from dotenv import load_dotenv
import os
import requests
from random import randint


def get_random_img():
    main_response = requests.get('https://xkcd.com/info.0.json')
    main_response.raise_for_status()
    num_img = main_response.json()['num']
    img_number = randint(0, num_img)
    response = requests.get(f'https://xkcd.com/{img_number}/info.0.json')
    image = requests.get(response.json()['img'])
    image.raise_for_status()
    img_comment = response.json()['alt']
    img_name = 'comic.png'
    with open(img_name, 'wb') as file:
        file.write(image.content)
    return img_name, img_comment


def get_upload_url(access_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {'group_id': group_id,
               'access_token': access_token}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    return upload_url


def upload_img_to_server(img_name, url_for_upload):
    with open(img_name, 'rb') as file:
        files = {'photo': file}
        response = requests.post(url_for_upload, files=files)
    response.raise_for_status()
    saved_img = response.json()
    server = saved_img['server']
    hash_img = saved_img['hash']
    photo = saved_img['photo']
    return server, hash_img, photo


def upload_img_to_wall(group_id, access_token, server, hash_img, photo):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {'group_id': group_id,
               'server': server,
               'photo': photo,
               'hash': hash_img,
               'access_token': access_token,
               'v': '5.131'}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    uploaded_img = response.json()
    owner_id = uploaded_img.get('response')[0]['owner_id']
    media_id = uploaded_img.get('response')[0]['id']
    return owner_id, media_id


def publish_img_to_wall(group_id, img_comment, access_token, owner_id, media_id):
    url = f"https://api.vk.com/method/wall.post"
    payload = {'owner_id': f'-{group_id}',
               'from_group': 1,
               'attachments': f'photo{owner_id}_{media_id}',
               'message': img_comment,
               'access_token': access_token,
               'v': '5.131'}
    response = requests.post(url, params=payload)
    response.raise_for_status()


def main():
    load_dotenv()
    access_token = os.environ['VK_TOKEN']
    group_id = os.environ['GROUP_ID']

    img_name, img_comment = get_random_img()
    try:
        url_for_upload = get_upload_url(access_token, group_id)
        server, hash_img, photo = upload_img_to_server(img_name, url_for_upload)
        owner_id, media_id = upload_img_to_wall(group_id, access_token, server, hash_img, photo)
        publish_img_to_wall(group_id, img_comment, access_token, owner_id, media_id)
    except requests.exceptions.HTTPError:
        print(traceback.format_exc())
    finally:
        os.remove(img_name)


if __name__ == '__main__':
    main()