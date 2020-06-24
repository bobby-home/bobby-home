from tasks import send_message

print('RUN TASK !')
send_message.delay('Hello world')
