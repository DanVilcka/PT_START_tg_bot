import logging
import re
from pathlib import Path

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import os
import paramiko
from dotenv import load_dotenv

import psycopg2

# dotenv_path = Path(__file__).parent.parent.joinpath('.env')
# load_dotenv(dotenv_path)

load_dotenv()

TOKEN = os.getenv('TOKEN')

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

host_db = os.getenv('HOST_POSTGRES')
port_db = os.getenv('PORT_POSTGRES')
username_db = os.getenv('USERNAME_POSTGRES')
password_db = os.getenv('PASSWORD_POSTGRES')

# Подключаем логирование
logging.basicConfig(
    filename='../logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=host, username=username, password=password, port=port)

client_db = paramiko.SSHClient()
client_db.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_db.connect(hostname=host_db, username=username_db, password=password_db, port=port_db)

db = psycopg2.connect("host=localhost dbname=contacts user=postgres password=postgres")
cur = db.cursor()


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'[+]?\d{1}[- ]?[(]?\d{3}[)]?[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}')
    # re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}')  # формат 8 (000) 000-00-00
    # re.compile(r'([+]?\d{1})[- ]?([(]?\d{3}[)]?)[- ]?(\d{3})[- ]?(\d{2})[- ]?(\d{2})')
    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    update.message.reply_text('Информация будет записана в базу данных')

    for i in range(len(phoneNumberList)):
        try:
            cur.execute("INSERT INTO Phones (ID, Phone) VALUES (%s, %s)", (i + 1, str(phoneNumberList[i])))
            update.message.reply_text(f'Информация о почте {phoneNumberList[i]} была записана в базу данных!')
        except:
            update.message.reply_text('Ошибка записи')
    return ConversationHandler.END

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')

    return 'findEmail'

def findEmail(update: Update, context):
    user_input = update.message.text  # Получаем текст

    EmailRegex = re.compile(r'\w+@\w+\.\w+')
    EmailsList = EmailRegex.findall(user_input)

    if not EmailsList:
        update.message.reply_text('Почтовые адреса не найдены')
        return ConversationHandler.END

    emails = ''
    for i in range(len(EmailsList)):
        emails += f'{i + 1}. {EmailsList[i]}\n'

    update.message.reply_text(emails)
    update.message.reply_text('Информация будет записана в базу данных')

    for i in range(len(EmailsList)):
        try:
            cur.execute("INSERT INTO Emails (ID, Email) VALUES (%s, %s)", (int(i+1), str(EmailsList[i])))
            update.message.reply_text(f'Информация о почте {EmailsList[i]} была записана в базу данных!')
        except:
            update.message.reply_text('Ошибка записи')
    return ConversationHandler.END

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите текст для проверки пароля: ')

    return 'verifyPassword'


def verifyPassword(update: Update, context):
    user_input = update.message.text  # Получаем текст

    passwordRegex = re.compile(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z!@#$%^&*()]{8,}$')

    password = ''
    if bool(passwordRegex.match(user_input)):
        update.message.reply_text('Пароль сложный')
        return ConversationHandler.END
    else:
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END


def getRelease(update: Update, context):
    stdin, stdout, stderr = client.exec_command('uname -r')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getUname(update: Update, context):
    stdin, stdout, stderr = client.exec_command('hostnamectl')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getUptime(update: Update, context):
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getDf(update: Update, context):
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getFree(update: Update, context):
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getMpstat(update: Update, context):
    stdin, stdout, stderr = client.exec_command('mpstat | head -n100')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getW(update: Update, context):
    stdin, stdout, stderr = client.exec_command('who -u')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getAuths(update: Update, context):
    stdin, stdout, stderr = client.exec_command('last | head -n100')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getCritical(update: Update, context):
    stdin, stdout, stderr = client.exec_command('journalctl -p 2 | head -n5')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getPs(update: Update, context):
    stdin, stdout, stderr = client.exec_command('ps aux | head -n100')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getSs(update: Update, context):
    stdin, stdout, stderr = client.exec_command('ss | head -n100')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getServices(update: Update, context):
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type service --state running')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getAppListCommand(update: Update, context):
    update.message.reply_text('Введите название пакета или команду all: ')

    return 'getAppList'


def getAppList(update: Update, context):
    user_input = update.message.text  # Получаем текст

    if str(user_input).lower() == 'all':
        stdin, stdout, stderr = client.exec_command('apt list | head -n100')
        data = stdout.read() + stderr.read()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
        return ConversationHandler.END
    else:
        stdin, stdout, stderr = client.exec_command('apt show ' + user_input)
        data = stdout.read() + stderr.read()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
        return ConversationHandler.END


def getReplLogs(update: Update, context):
    stdin, stdout, stderr = client_db.exec_command('cat /usr/local/var/log/postgresql@16.log | head -n20')
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def getEmails(update: Update, context):
    ans = 'Список почт: \n'
    cur.execute("SELECT * FROM Emails")
    emails = cur.fetchall()
    for email in emails:
        ans += str(email[0]) + ' - ' + str(email[1]) + '\n'
    update.message.reply_text(ans)
    return ConversationHandler.END


def getPhoneNumbers(update: Update, context):
    ans = 'Список телефонов: \n'
    cur.execute("SELECT * FROM Phones")
    phones = cur.fetchall()
    for phone in phones:
        ans += str(phone[0]) + ' - ' + str(phone[1]) + '\n'
    update.message.reply_text(ans)
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerGetAppLIst = ConversationHandler(
        entry_points=[CommandHandler('get_app_list', getAppListCommand)],
        states={
            'getAppList': [MessageHandler(Filters.text & ~Filters.command, getAppList)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(CommandHandler('get_repl_logs', getReplLogs))
    dp.add_handler(CommandHandler('get_emails', getEmails))
    dp.add_handler(CommandHandler('get_phone_numbers', getPhoneNumbers))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerGetAppLIst)

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
