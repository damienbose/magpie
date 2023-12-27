all: reset install_data

reset:
	rm -rf archives
	mkdir -p archives

install_data:
	wget 'https://github.com/bloa/tevc_2020_artefact/releases/download/v1.0-archives/sat_uniform.tar.gz' -O archives/sat_uniform.tar.gz
	tar xzf archives/sat_uniform.tar.gz -C examples/code/minisat/data
	rm -rf archives


