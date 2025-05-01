from flask import Flask, render_template, request, jsonify
import requests

API_KEY = "d283bba8274e23d8365ed5ef87d60587"
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def fetch_movie_info(title):
    search_url = f'{TMDB_BASE_URL}/search/movie'
    search_params = {'api_key': API_KEY, 'query': title, 'language': 'ja-JP'}
    res = requests.get(search_url, params=search_params).json()

    if not res['results']:
        return None

    movie_id = res['results'][0]['id']
    detail_url = f'{TMDB_BASE_URL}/movie/{movie_id}'
    detail_params = {
        'api_key': API_KEY,
        'language': 'ja-JP',
        'append_to_response': 'credits,recommendations'
    }
    data = requests.get(detail_url, params=detail_params).json()

    director = next(
        (member['name'] for member in data['credits']['crew'] if member['job'] == 'Director'),
        '不明'
    )

    return {
        'title': data.get('title'),
        'year': data.get('release_date', '')[:4],
        'overview': data.get('overview'),
        'rating': data.get('vote_average'),
        'genres': [g['name'] for g in data.get('genres', [])],
        'poster_path': data.get('poster_path'),
        'director': director,
        'cast': [{
            'name': c['name'],
            'profile': f"https://image.tmdb.org/t/p/w200{c['profile_path']}" if c['profile_path'] else None
        } for c in data['credits']['cast'][:5]],
        'recommendations': [r['title'] for r in data['recommendations']['results'][:3]]
    }

def fetch_suggestions(query):
    url = f'{TMDB_BASE_URL}/search/movie'
    params = {'api_key': API_KEY, 'query': query, 'language': 'ja-JP'}
    res = requests.get(url, params=params).json()
    suggestions = [movie['title'] for movie in res.get('results', [])[:5]]
    return suggestions

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    info = None
    if request.method == 'POST':
        title = request.form['title']
        info = fetch_movie_info(title)
        if not info:
            return render_template('index.html', error='映画情報が見つかりませんでした。', info=info)
        return render_template('result.html', info=info)
    return render_template('index.html', info=info)

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '')
    suggestions = fetch_suggestions(query)
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
