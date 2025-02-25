from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    """
    创建Flask应用实例
    
    @return {Flask} app - Flask应用实例
    """
    load_dotenv()  # 加载环境变量
    app = Flask(__name__)
    CORS(app)
    
    # 注册蓝图
    from app.routes.api import api_bp
    from app.routes.customer_service import cs_bp
    from app.routes.travel.planner import travel_bp
    from app.routes.travel.train import train_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(cs_bp, url_prefix='/api/cs')
    app.register_blueprint(travel_bp, url_prefix='/api/travel')
    app.register_blueprint(train_bp)
    
    return app 