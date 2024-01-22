import telebot
import config
import pb
import datetime
import pytz
import json
import traceback
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from theblockchainapi import SolanaAPIResource, SolanaNetwork


RESOURCE = SolanaAPIResource(
   api_key_id='2nOnCrK5W5r8x3z',
   api_secret_key='h2skAfaxVIBJRpS'
)

endpoint="https://api.mainnet-beta.solana.com"

solana_client = Client(endpoint)

P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
      telebot.types.InlineKeyboardButton(text='🌟 Wallet Tracking', callback_data='Wallet Tracking')
    )
    keyboard.add(
      telebot.types.InlineKeyboardButton('🌟Token Tracking', callback_data='Token Tracking')
    )
    keyboard.add(
      telebot.types.InlineKeyboardButton('🌟Liquidity Pool Tracking', callback_data='Liquidity Pool Tracking')
    )
    keyboard.add(
      telebot.types.InlineKeyboardButton('🌟Swap Tracking', callback_data='Swap Tracking')
    )

    bot.send_message(message.chat.id, 'Choose what to do now:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call:True)
def iq_callback(query):
    data = query.data
    if data.startswith('Wallet Tracking'):
       get_wallet_callback(query)
    if data.startswith('Cancel'):
        bot.delete_message(query.message.chat.id, query.message.message_id)
        
        

def get_wallet_callback(query):
    bot.answer_callback_query(query.id)
    bot.send_chat_action(query.message.chat.id, 'typing')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Cancel',callback_data='Cancel'),
    )
    bot.send_message(
        query.message.chat.id, 'Input the Solana Wallet address',
        reply_markup=keyboard
    )
    @bot.message_handler(func=lambda message: True)
    def handle_text(message):
      address = message.text
      tkn_pub_key  = Pubkey.from_string(address)
      account_info = solana_client.get_account_info(tkn_pub_key)
      if account_info:
          balance_lamports = account_info.value.lamports
          balance_sol = balance_lamports / 10**9
      else:
          print("Error fetching balance")
      bot.send_message(query.message.chat.id, 'The balance of wallet is '+str(balance_sol))
      
      signatures = solana_client.get_signatures_for_address(tkn_pub_key, limit=10)
      final_output = "Transactions:"+'\n'
      for i in range(0,10):
        final_output+= str(signatures.value[i].signature)+'\n'
      bot.send_message(query.message.chat.id, final_output)

      result = RESOURCE.get_wallet_token_holdings(
         public_key=address,
         network=SolanaNetwork.MAINNET_BETA
      )
      
      token_output = "Token holdings:"+'\n'
      for i in range(0,10):
         token_output+= str(result[i])+'\n'
      bot.send_message(query.message.chat.id,token_output)
      #tokens=solana_client.get_token_accounts(tkn_pub_key,TokenAccountOpts(program_id=Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')))
      #print(tokens)

bot.polling(non_stop=True)


