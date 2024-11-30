import vk_api
from datetime import datetime

class Post:
	_message: str
	_attachments: list[str]
	_donut_paid_duration: int
	_publish_date: int
	_params: dict[str, any]
	
	def __init__(self, group_id: int, vk_api: vk_api.VkApi) -> None:
		self._group_id = group_id
		self._vk_api = vk_api

		self._message = ""
		self._attachments = []
		self._donut_paid_duration = 0
		self._publish_date = 0
		self._params = {}

	def add_attachment(self, att_type: str, owner_id: int, media_id: int):
		self._attachments.append({
			'type' : att_type,
			'owner_id' : owner_id,
			'media_id' : media_id,
		})

	def set_publish_date(self, date: datetime):
		self._publish_date = date.timestamp()
	
	def set_params(self, **kwargs):
		self._params.update(kwargs)
	
	def set_message(self, msg: str):
		self._message = msg

	def set_donut_paid_duration(self, duration: int):
		self._donut_paid_duration = duration

	def parse_attachments(self):
		res = []
		for attachment in self._attachments:
			res.append(f"{attachment['type']}{attachment['owner_id']}_{attachment['media_id']}")
		
		return ','.join(res)

	def get_data(self) -> dict[str, any]:
			return  {
				'message': self._message,
				'attachments' : self.parse_attachments(),
				'publish_date': self._publish_date,
				**self._params
			}
	
	def publish(self):
		self._vk_api.wall.post(from_group=1, owner_id=-self._group_id, **self.get_data())

class PostFactory:
	_vk_session: vk_api.VkApi

	def __init__(self, token):
		self._vk_session = vk_api.VkApi(token=token)

	def create_post(self, group_id: int, msg: str, photo_paths: list[str] = []):
		post = Post(group_id=group_id, vk_api = self._vk_session.get_api())
		post._message = msg

		upload = vk_api.VkUpload(self._vk_session)
		for img in photo_paths:
			photo = upload.photo_wall(
				img,
				group_id=group_id
			)[0]

			post.add_attachment('photo', photo['owner_id'], photo['id'])

		return post