---
marp: true
theme: default
paginate: true
math: mathjax
style: |
  section { font-family: 'Helvetica', 'Arial', sans-serif; font-size: 30px; }
  h1 { color: #1f4e79; }
  h2 { color: #2980b9; border-bottom: 2px solid #bdc3c7; padding-bottom: 10px; }
  table { width: 100%; font-size: 24px; }
  th { background-color: #ecf0f1; }
---

# O Vento
### **Capítulo 2**
##### Laiza Edwigens Rocha Silva, sob número de matrícula 554328

---

## 2.1 Escalas de Movimento do Ar

Os deslocamentos atmosféricos variam em duração e tamanho. Em meteorologia, agrupam-se em quatro escalas principais:

| Escala | Tempo | Comprimento [km] | Exemplos |
|---|---|---|---|
| **Circulação Geral** | Semanas a anos | 1.000 a 40.000 | Correntes de vento, ventos alísios |
| **Sinóptica** | Dias a semanas | 100 a 5.000 | Ciclones, anticiclones, furacões |
| **Mesoescala** | Minutos a dias | 1 a 100 | Tornados, temporais, brisas |
| **Microescala** | Segundos a minutos | < 1 | Turbulências, rajadas |

---

## 2.2 Radiação Solar e Terrestre

O sol aquece a superfície da Terra de forma desigual, provocando os fluxos de vento.

* **Albedo:** É o índice de absorção, definido como a relação entre a radiação refletida pela superfície e o fluxo incidente.
  * *Neve:* 70-95%
  * *Dunas:* 24-37%
  * *Oceanos:* 2-7%
* A transferência de calor para a atmosfera ocorre por condução e, de forma mais predominante, por **convecção** (intercâmbio vertical de massas de ar).

---

## 2.3 Movimento e Gradiente de Pressão

O aquecimento diferenciado provoca gradientes de pressão atmosférica. O ar tende a se mover de uma zona de **alta pressão** para uma de **baixa pressão**.

A força do gradiente de pressão horizontal resultante ($F_x$) por unidade de massa é dada por:

$$ F_x = -\left(\frac{1}{\rho}\frac{\Delta P}{\Delta x}\right) $$

Onde:
* $\rho$ = massa específica do ar
* $\Delta P$ = diferença de pressão
* $\Delta x$ = distância (comprimento do volume de ar)
*OBS: O sinal negativo indica que a força atua na direção de diminuir a pressão.*


---

## 2.4 A Força de Coriolis

Efeito gerado pela rotação da Terra que desvia os objetos em movimento livre, incluindo os ventos.

* **Hemisfério Sul:** Os ventos são desviados para a **esquerda**.
* **Hemisfério Norte:** Os ventos são desviados para a **direita**.

A equação por unidade de massa é:

$$ C = 2 \Omega v \sin\varphi $$

*( $\Omega$ = vel. angular da Terra, $v$ = vel. da partícula, $\varphi$ = latitude )*

---

## 2.5 O Vento Geostrófico

Ocorre na atmosfera superior, onde o atrito com o solo é nulo. Acontece quando há um balanço (equilíbrio) entre a força de gradiente de pressão ($F_x$) e a força de Coriolis ($C$).

Nesta situação, o vento sopra **paralelo às linhas isóbaras**.

$$ F_x = C \implies \frac{1}{\rho}\frac{\Delta P}{\Delta x} = 2 \Omega v \sin\varphi $$

---

## 2.6 O Vento de Gradiente: Ciclones e Anticiclones

Quando os fluxos seguem rotas curvas, surge a **Força Centrífuga** ($F_c = \frac{v^2}{r}$).

* **Ciclones (Baixa Pressão):** 
  * Equilíbrio: $F_x = C + F_c$
  * Rotação: Horária no Sul, Anti-horária no Norte. Devido ao atrito na superfície, o ar forma uma espiral convergente.
* **Anticiclones (Alta Pressão):**
  * Equilíbrio: $C = F_x + F_c$
  * Rotação: Anti-horária no Sul, Horária no Norte. Na superfície, o ar forma uma espiral divergente (para fora).

---

## 2.7 A Circulação Geral do Vento

Causada pelo aquecimento maior no Equador e menor nos polos. O balanço idealizado cria três células de circulação por hemisfério:

1. **Célula Tropical:** Gera os ventos alísios (Sudeste no HS, Nordeste no HN) convergindo para a região equatorial.
2. **Célula Temperada:** Predomínio de ventos de oeste (noroeste no HS, sudoeste no HN).
3. **Célula Polar:** Formada por um anticiclone polar que gera ventos de leste.

---

## 2.8 Circulação Secundária

Fenômenos atmosféricos em larga escala (menores que a circulação geral) ligados aos centros de pressão.

* **Furacões:** Ciclones tropicais intensos (ventos > 80 m/s). Derivam energia do calor latente liberado pela condensação do vapor d'água oceânico.
* **Monções:** Ocorrem pela diferença sazonal de pressão entre continente (muito aquecido no verão, frio no inverno) e oceano.
* **Ciclones Extratropicais:** Formados na interface (frentes) de massas de ar com densidades/temperaturas diferentes.

---

## 2.9 Circulações Terciárias (Regionais)

Circulações locais de pequena escala, cruciais para o estudo de energia eólica.

* **Brisas Marítimas/Terrestres:** 
  * Dia: Terra mais quente que a água $\rightarrow$ vento flui do mar para a terra.
  * Noite: Terra esfria rápido $\rightarrow$ vento inverte, da terra para o mar.
* **Ventos de Vales e Montanhas:** Durante o dia, o ar aquece e sobe a encosta; à noite, o processo se inverte e o ar frio (mais denso) desce para o vale.
