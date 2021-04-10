jupyter-lab \
  --ip=0.0.0.0
  --port=8888 \
  --ContentsManager.allow_hidden=True \
  --ServerApp.password $JUPYTER_PASSWORD_HASH \
  --notebook-dir=/workspace \
  --no-browser \
  --allow-root
