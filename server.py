from app import Site

site = Site()

if __name__ == '__main__':
    site.run(host='0.0.0.0', debug=True, port=5000)
