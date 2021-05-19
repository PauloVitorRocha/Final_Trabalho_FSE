# Projeto Final
## Fundamentos de Sistemas Embarcados

**Nome**: Paulo Vítor Coelho da Rocha

**Matrícula**: 17/0062465

Para detalhes de como funciona o projeto, assista o [video](https://youtu.be/c-ymt3ST6hE)

### Executando o projeto
```
git clone https://github.com/PauloVitorRocha/Final_Trabalho_FSE.git
```

#### Primeiramente para o servidor:
```
cd Final_Trabalho_FSE/sv
pip3 install -r requirements.txt
```
após a instalação dos requirements basta rodar:
```
python3 sv.py
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

