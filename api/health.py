from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'xiaohongshu-publish-api',
        'version': '1.0.0'
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
