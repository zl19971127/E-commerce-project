from fdfs_client.client import Fdfs_client

client = Fdfs_client('client.conf')

a = client.upload_by_filename('/home/python/Desktop/images/1.jpg')
print(a)

# from fdfs_client.client import Fdfs_client
#
# client = Fdfs_client("client.conf")
#
# data = client.upload_by_filename('/home/python/Desktop/1.jpg')
