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
    response.raise_for_status()
    return response.json()


def download_image(response):
    image = requests.get(response['img'])
    image.raise_for_status()
    img_name = 'comic.png'
    with open(img_name, 'wb') as file:
        file.write(image.content)
    return img_name


def get_upload_url(access_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {'group_id': group_id,
               'access_token': access_token}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    return upload_url


def upload_img_to_server(img_name, access_token, group_id):
    with open(img_name, 'rb') as file:
        files = {'photo': file}
        url_for_upload = get_upload_url(access_token, group_id)
        response = requests.post(url_for_upload, files=files)
        response.raise_for_status()
        server = response.json()['server']
        hash = response.json()['hash']
        photo = response.json()['photo']
        return server, hash, photo


def upload_img_to_wall(group_id, img_name, access_token, api_version):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    server, hash, photo = upload_img_to_server(img_name, access_token, group_id)
    payload = {'group_id': group_id,
               'server': server,
               'photo': photo,
               'hash': hash,
               'access_token': access_token,
               'v': api_version}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    owner_id = response.json().get('response')[0]['owner_id']
    media_id = response.json().get('response')[0]['id']
    return owner_id, media_id


def publish_img_to_wall(group_id, img_comment, access_token, api_version):
    url = f"https://api.vk.com/method/wall.post"
    owner_id, media_id = upload_img_to_wall(group_id, access_token, api_version)
    payload = {'owner_id': f'-{group_id}',
               'from_group': 1,
               'attachments': f'photo{owner_id}_{media_id}',
               'message': img_comment,
               'access_token': access_token,
               'v': api_version}
    response = requests.post(url, params=payload)
    response.raise_for_status()


def main():
    load_dotenv()
    access_token = os.environ['VK_TOKEN']
    group_id = os.environ['GROUP_ID']
    api_version = os.environ['API_VERSION']

    img_response = get_random_img()
    img_comment = img_response['alt']
    img_name = download_image(img_response)
    publish_img_to_wall(group_id, img_comment, access_token, api_version)
    os.remove(img_name)


if __name__ == '__main__':
    main()