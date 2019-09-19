from fdfs_client.client import Fdfs_client

client = Fdfs_client('client.conf')

a = client.upload_by_filename('/home/python/Desktop/meizi.jpg')
print(a)

