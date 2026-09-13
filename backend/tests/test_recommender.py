import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.data import load_movies, content_features
from backend.app.recommender import Recommender

@pytest.fixture(scope='module')
def model():
    return Recommender(load_movies())

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c

def test_search(model):
    assert model.search('INTERSTELLAR')[0]['title'] == 'Interstellar'
    assert model.search('  ') == []
    assert model.search('zzzznoresults') == []
    assert len(model.search('star', limit=3)) == 3

def test_recommendation_ranking_and_exclusion(model):
    ids = [model.search('Interstellar')[0]['id'], model.search('Inception')[0]['id']]
    results = model.recommend(ids)
    assert len(results) == 10
    assert not set(ids) & {movie['id'] for movie in results}
    scores = [movie['score'] for movie in results]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= score <= 1 for score in scores)
    assert len({movie['id'] for movie in results}) == 10
    assert model.recommend(ids + [ids[0]]) == results

def test_scores_match_manual_cosine(model):
    ids = [1, 2]
    result = model.recommend(ids, 1)[0]
    taste = np.asarray(model.matrix[[model.id_to_index[mid] for mid in ids]].mean(axis=0)).ravel()
    movie = model.matrix[model.id_to_index[result['id']]].toarray().ravel()
    expected = float(np.dot(taste, movie) / (np.linalg.norm(taste) * np.linalg.norm(movie)))
    assert result['score'] == pytest.approx(expected)
    assert sum(f['contribution'] for f in result['shared_features']) <= result['score'] + 1e-12

def test_unknown_id(model):
    with pytest.raises(ValueError, match='Unknown'):
        model.recommend([99999999])

def test_empty_selection(model):
    with pytest.raises(ValueError):
        model.recommend([])

def test_features():
    assert content_features('Space (Test)', ['Sci-Fi']).split() == ['scifi', 'scifi', 'scifi', 'space', 'test']

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['movies'] > 9000

def test_api_search(client):
    assert client.get('/movies/search?q=interstellar').json()[0]['title'] == 'Interstellar'
    assert client.get('/movies/search?q=').status_code == 422

def test_api_recommend(client):
    response = client.post('/recommend', json={'movie_ids':[1,2], 'limit':10})
    assert response.status_code == 200
    assert len(response.json()['recommendations']) == 10
    assert client.post('/recommend', json={'movie_ids':[9999999]}).status_code == 400

@pytest.mark.parametrize('body', [{'movie_ids':[]}, {'movie_ids':[1], 'limit':0}, {'movie_ids':[1], 'limit':21}, {'movie_ids':[1,2,3,4,5,6]}, {'movie_ids':['1']}, {'movie_ids':[True]}, {'movie_ids':[-1]}])
def test_validation(client, body):
    assert client.post('/recommend', json=body).status_code == 422

def test_tmdb_failure_is_optional(monkeypatch):
    from backend.app.enrichment import enrich, details
    import httpx
    monkeypatch.setenv('TMDB_API_KEY','test-only-not-real')
    def failure(*args, **kwargs):
        raise httpx.ConnectError('offline')
    monkeypatch.setattr(httpx, 'get', failure)
    details.cache_clear()
    movies = load_movies()
    movie = Recommender(movies).movie(0)
    assert enrich(movie, movies) == movie

def test_presentation_format_not_a_feature(model):
    assert 'imax' not in model.vectorizer.vocabulary_
    assert all('IMAX' not in genres for genres in model.movies.genres)

@pytest.fixture(scope='module')
def catalog_model():
    from backend.app.data import load_catalog
    return Recommender(load_catalog())

def test_series_search_and_namespaces(catalog_model):
    from backend.app.data import SERIES_ID_OFFSET
    results = catalog_model.search('Breaking Bad')
    show = next(item for item in results if item['media_type'] == 'series')
    assert show['id'] >= SERIES_ID_OFFSET
    assert show['overview'] and '<p>' not in show['overview']
    assert show['source_url'].startswith('https://www.tvmaze.com/')
    assert catalog_model.movies.movieId.is_unique

def test_mixed_favorites_and_type_filters(catalog_model):
    movie = catalog_model.search('Interstellar')[0]
    series = next(item for item in catalog_model.search('Breaking Bad') if item['media_type'] == 'series')
    ids = [movie['id'], series['id']]
    for media_type in ('all', 'movie', 'series'):
        results = catalog_model.recommend(ids, 10, media_type)
        assert len(results) == 10
        assert not set(ids) & {item['id'] for item in results}
        assert [item['score'] for item in results] == sorted([item['score'] for item in results], reverse=True)
        if media_type != 'all':
            assert all(item['media_type'] == media_type for item in results)

def test_series_api(client):
    response = client.get('/titles/search?q=Breaking%20Bad')
    assert response.status_code == 200
    show = next(item for item in response.json() if item['media_type'] == 'series')
    results = client.post('/recommend', json={'movie_ids':[show['id']], 'media_type':'series'}).json()['recommendations']
    assert len(results) == 10
    assert all(item['media_type'] == 'series' and item['id'] != show['id'] for item in results)
    assert client.post('/recommend', json={'movie_ids':[1], 'media_type':'invalid'}).status_code == 422
    assert client.get('/health').json()['series'] > 0

def test_series_enrichment_never_calls_movie_api(monkeypatch):
    import httpx
    from backend.app.enrichment import enrich
    monkeypatch.setenv('TMDB_API_KEY', 'test-only')
    def unexpected(*args, **kwargs):
        pytest.fail('Series must not call the TMDB movie endpoint')
    monkeypatch.setattr(httpx, 'get', unexpected)
    series = {'id':1000000001,'media_type':'series','overview':'Example'}
    assert enrich(series, None) == series

def test_netflix_original_catalog_and_filter(catalog_model):
    stranger_things = next(item for item in catalog_model.search('Stranger Things')
                           if item['media_type'] == 'series')
    assert stranger_things['netflix_original'] is True
    assert stranger_things['platform'] == 'Netflix'
    results = catalog_model.recommend([stranger_things['id']], 10, 'netflix')
    assert len(results) == 10
    assert all(item['media_type'] == 'series' and item['netflix_original'] for item in results)
    assert stranger_things['id'] not in {item['id'] for item in results}
