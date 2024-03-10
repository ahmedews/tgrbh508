import os,certifi
from pyrogram import Client,errors
import telebot
import threading
from telebot import types
import asyncio
from backend import app
from db import database

DB = database()
App = app()
os.environ['SSL_CERT_FILE'] = certifi.where() 
api_id = '26281496'
api_hash = 'a9b8db3efd4be04118d0391f124982c7'
TELEGRAM_TOKEN="6371348575:AAEREntO0tT8gHF6m4zOZ7auzgR-W7CVycg" 
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False,num_threads=55,skip_pending=True)
@bot.message_handler(commands=['start'])
def Admin(message):
    AddAccount=types.InlineKeyboardButton("اضافه حساب 🛎",callback_data="AddAccount")
    Accounts=types.InlineKeyboardButton("اكواد حساباتك 🖲",callback_data="Accounts")
    a1=types.InlineKeyboardButton("نقل اعضاء 👤😇",callback_data="a1")
    inline = types.InlineKeyboardMarkup(keyboard=[[a1],[AddAccount],[Accounts]])
    bot.send_message(message.chat.id,"""*مرحبا بك  👋

اختار ما تريد من الازار اسفل 🔥
يمكنك نقل اعضاء لجروبك 🛎
من اي جروب اخر عام  ☄

Creator : @amrakl *""",reply_markup=inline ,parse_mode="markdown")

@bot.callback_query_handler(lambda call:True)
def call(call):
    if call.data =="Accounts":
        num = DB.accounts()
        msg=bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=f"حساباتك المسجلة بلكامل : {num}",parse_mode="markdown")
    if call.data =="AddAccount":
        msg=bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="*قوم بارسال الرقم الذي تريد تسليمه مع رمز الدولة الان*📞🎩",parse_mode="markdown")
        bot.register_next_step_handler(msg, AddAccount)
    if call.data =="a1":
        msg=bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="*قوم بارسال رابط الجروب المراد النقل منه *🖲",parse_mode="markdown")
        bot.register_next_step_handler(msg, statement)
def statement(message):
    Fromgrob = message.text
    msg =bot.send_message(chat_id=message.chat.id,text="*قوم بارسال رابط الجروب المراد النقل له*🛎",parse_mode="markdown")
    bot.register_next_step_handler(msg, statement2,Fromgrob)
def statement2(message,Fromgrob):
    Ingrob = message.text
    msg=bot.send_message(chat_id=message.chat.id,text="*انتظر قليلا ⏱*",parse_mode="markdown")
    T = threading.Thread(target=asyncio.run,args=(App.GETuser(Fromgrob,Ingrob),))
    T.start()
    T.join()
    list = T.return_value
    numUser = len(list)
    bot.send_message(message.chat.id,f"""*تم حفظ جميع الاعضاء المتاحه بنجاح *✅

*معلومات عملية النقل 🥸😇

 الاعضاء المتاحه : {numUser} عضو 😋
النقل من  : {Fromgrob} 🎒
النقل الي : {Ingrob} 🧳
مده الفحص : 1 ثانية ⏱

انتظر الي ان تتم العملية 🎩* """ ,parse_mode="markdown")
    T = threading.Thread(target=asyncio.run,args=(App.ADDuser(list,Ingrob,message.chat.id,bot),))
    T.start()
def AddAccount(message):
    try:         
        if "+" in message.text:
            bot.send_message(message.chat.id,"*انتظر جاري الفحص* ⏱",parse_mode="markdown")
            _client = Client("::memory::", in_memory=True,api_id=api_id, api_hash=api_hash,lang_code="ar")
            _client.connect()
            SendCode = _client.send_code(message.text)
            Mas = bot.send_message(message.chat.id,"*أدخل الرمز المرسل إليك 🔏*",parse_mode="markdown")
            bot.register_next_step_handler(Mas, sigin_up,_client,message.text,SendCode.phone_code_hash,message.text)	
        else:
            Mas = bot.send_message(message.chat.id,"*انتظر جاري الفحص* ⏱")
    except Exception as e:
        bot.send_message(message.chat.id,"ERORR : "+e)
def sigin_up(message,_client,phone,hash,name):
    try:
        bot.send_message(message.chat.id,"*انتظر قليلا ⏱*",parse_mode="markdown")
        _client.sign_in(phone, hash, message.text)
        bot.send_message(message.chat.id,"*تم تاكيد الحساب بنجاح ✅ *",parse_mode="markdown")
        ses= _client.export_session_string()
        DB.AddAcount(ses,name,message.chat.id)
    except errors.SessionPasswordNeeded:
        Mas = bot.send_message(message.chat.id,"*أدخل كلمة المرور الخاصة بحسابك 🔐*",parse_mode="markdown")
        bot.register_next_step_handler(Mas, AddPassword,_client,name)	
def AddPassword(message,_client,name):
    try:
        _client.check_password(message.text) 
        ses= _client.export_session_string()
        DB.AddAcount(ses,name,message.chat.id)
        try:
            _client.stop()
        except:
            pass
        bot.send_message(message.chat.id,"*تم تاكيد الحساب بنجاح ✅ *",parse_mode="markdown")
    except Exception as e:
        print(e)
        try:
            _client.stop()
        except:
            pass
        bot.send_message(message.chat.id,f"ERORR : {e} ")
bot.infinity_polling(none_stop=True,timeout=15, long_polling_timeout =15)