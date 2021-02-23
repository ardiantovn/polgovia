mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
maxUploadSize=5140\n\
\n\
" > ~/.streamlit/config.toml
