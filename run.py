from app import create_app

"""
Flask应用程序入口点
"""

app = create_app()

if __name__ == '__main__':
    # 确保监听所有网络接口
    app.run(host='0.0.0.0', debug=True, port=5000) 