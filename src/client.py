import argparse
import statistics
import time
import requests
from common import ROOT, save_json

BODY = {'dataframe_records': [{'montant': 8500.0, 'anciennete': 3, 'freq_24h': 9, 'nuit': 1}]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?', default=8100)
    parser.add_argument('--repetition', type=int, default=1)
    args = parser.parse_args()
    url = f'http://127.0.0.1:{args.port}/invocations'

    def predict():
        response = requests.post(url, json=BODY, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('predictions') != [1]:
            raise RuntimeError(f'Prediction inattendue : {result}')
        return result

    response = predict()
    print('reponse : 200', response, flush=True)
    for _ in range(10):
        predict()
    latencies = []
    for _ in range(200):
        t0 = time.perf_counter()
        predict()
        latencies.append((time.perf_counter() - t0) * 1000)
    result = {'port': args.port, 'repetition': args.repetition, 'warmup': 10, 'calls': 200,
              'response': response, 'median_ms': statistics.median(latencies),
              'p95_ms': statistics.quantiles(latencies, n=20)[18], 'latencies_ms': latencies}
    save_json(f'latence_{args.port}_{args.repetition}.json', result)
    print(f'port {args.port} | mediane : {result["median_ms"]:.2f} ms | p95 : {result["p95_ms"]:.2f} ms', flush=True)


if __name__ == '__main__':
    main()
