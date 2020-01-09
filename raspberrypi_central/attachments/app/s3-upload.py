import boto3

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#client
s3 = boto3.resource('s3')


# for bucket in s3.list_buckets():
#     print(bucket)

data = open('test.txt', 'rb')
s3.Bucket('my-bucket').put_object(Bucket='mx-documents', Key='test.txt', Body=data)
