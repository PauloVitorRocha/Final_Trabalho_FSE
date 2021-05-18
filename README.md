# Projeto Final
## Fundamentos de Sistemas Embarcados

**Nome**: Paulo Vítor Coelho da Rocha

**Matrícula**: 17/0062465

### Executando o projeto
```
git clone https://github.com/PauloVitorRocha/Final_Trabalho_FSE.git
```

#### Para a ESP32 use:
```
cd Final_Trabalho_FSE/3_trabalho
```
agora temos que configurar a wifi por meio do comando:
```
idf.py menuconfig
```
e por fim:
```
idf.py -p {PORT} flash monitor
```

#### Para o servidor:
```
cd Final_Trabalho_FSE/sv
pip install -r requirements.txt
```
após a instalação dos requirements basta rodar:
```
python3 sv.py
```
