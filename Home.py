import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv('.env')
from mongo_auth import Authenticate
from utils import *
import webbrowser
import numpy as np
import pandas as pd
import openai

# Streamlitページの設定
st.set_page_config(page_title="SaaS", page_icon=":house", layout="centered", initial_sidebar_state="auto", menu_items=None)

# 環境変数の読み込み

# メインタイトルの表示
st.markdown('# Your SaaS App')

# 認証機能の初期化
st.session_state['authenticator'] = Authenticate("coolcookiesd267", "keyd3214", 60)

# セッション状態のデフォルト値を設定（未設定の場合）
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'verified' not in st.session_state:
    st.session_state['verified'] = None

# 未認証かつ未確認の場合のログイン処理
if not st.session_state['authentication_status'] and not st.session_state['verified']:
    st.session_state['authenticator'].login('Login', 'main')
if 'summarized_text' not in st.session_state:
    st.session_state['summarized_text'] = ''
if 'translation' not in st.session_state:
    st.session_state['translation'] = ''

# 認証済みかつメール確認済みのユーザーに対する処理
if st.session_state['verified'] and st.session_state["authentication_status"]:
    st.session_state['authenticator'].logout('Logout', 'sidebar', key='123')

    openai.api_key = os.environ["OPENAI_API_KEY"]

    client = openai.Client(api_key=os.environ["OPENAI_API_KEY"])
    # ユーザーのメールアドレスがサブスクリプション済みかチェック
    st.session_state['subscribed'] = is_email_subscribed(st.session_state['email'])
    
    # サブスクリプション状態の表示
    if st.session_state.get('subscribed'):
        st.write('サブスクリプション済みです！')
    else:
        st.write('サブスクリプションしていません！')

    # 無料ツール
    st.write('このツールは無料で使用できます！')
    input1 = st.text_area('要約したいテキストをここに入力してください：')
    if st.button('要約') and input1 and input1 != '':
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {'role': 'system', 'content': f'あなたは役立つアシスタントです。'},
            {"role": "user", "content": f"以下の内容の要約を提供してください： \n ```{input1}```"}
        ],
        temperature=0.0)
        st.session_state['summarized_text'] = response.choices[0].message.content
        
    st.write(st.session_state['summarized_text'])

    # サブスクリプション限定ツール
    st.write('サブスクリプション限定ツール')

    st.write('サブスクライバーのみが使用できる特別なツールです！')
    input2 = st.text_area('翻訳したいテキストをここに入力してください：')
    language = st.text_input('翻訳先の言語を入力してください：')
    if st.button('翻訳') and input2 and language and input2 != '' and language != '':
        if not st.session_state.get('subscribed'):
            st.error('このツールを使用するにはサブスクリプションが必要です！')
            st.link_button('サブスクリプション', os.getenv('STRIPE_PAYMENT_URL'))
            #webbrowser.open_new_tab()
        else:
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {'role': 'system', 'content': f'あなたは役立つアシスタントです。'},
                {"role": "user", "content": f"以下のテキストを{language}に翻訳してください： \n 入力: ```{input2}```"}
            ],
            temperature=0.0)
            st.write(response)
            st.session_state['translation'] = response.choices[0].message.content
    
    st.write(st.session_state['translation'])

# パスワードは正しいがメールが未確認のユーザーに対する処理
elif st.session_state["authentication_status"] == True:
    st.error('パスワードは正しいですが、メールアドレスが確認されていません。確認リンクが記載されたメールを確認してください。メールを確認した後、このページを更新してログインしてください。')
    
    # メール確認の再送信ボタンを追加
    if st.session_state.get('email'):
        if st.button(f"{st.session_state['email']}に確認メールを再送信"):
            resend_verification(st.session_state['email'])

# ログイン認証情報が不正な場合の処理
elif st.session_state["authentication_status"] == False:
    st.error('ユーザー名/パスワードが正しくないか、存在しません。ログイン認証情報をリセットするか、以下で新規登録してください。')
    forgot_password()
    register_new_user()

# 新規ユーザーまたは認証状態がない場合の処理
elif st.session_state["authentication_status"] == None:
    st.warning('SaaSアプリは初めてですか？以下で登録してください。')
    register_new_user()
