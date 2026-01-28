# FP_Projecte-Flet-Actual
Nova versió del projecte FP amb la versió moderna de Flet
# 🎓 Projecte d'Orientació FP amb Intel·ligència Artificial

## 📌 Descripció
Aquest projecte té com a objectiu **democratitzar l'accés a l'orientació acadèmica de la Formació Professional (FP) a la Comunitat Valenciana** mitjançant l'ús d'**Intel·ligència Artificial Generativa (LLM)**.

L'aplicació transforma el catàleg estàtic de la Generalitat Valenciana en una **eina conversacional interactiva**, capaç d'oferir orientació personalitzada, fiable i actualitzada.

---

## 🎯 Objectius del Projecte

- 🤖 Crear una experiència conversacional natural per orientar estudiants.
- 📚 Proporcionar informació oficial i actualitzada sobre FP.
- 🧭 Ajudar en la presa de decisions acadèmiques i professionals.
- 🌍 Garantir accés universal a l'orientació educativa.

---

## 👥 Equip de Treball

### Cristian Espinosa Vicens
- Arquitecte de dades (MySQL, curació FP)
- Responsable de Backend i Cloud
- Tecnologies: **Node.js, Amazon Bedrock**

### José Miguel Cendán Cabanilles
- Arquitecte de dades (MySQL, curació FP)
- Responsable de Frontend i UX
- Tecnologies: **Flet (Python)**

---

## 🧠 Funcionalitats Principals

- 💬 **Xat intel·ligent** tipus assistent virtual.
- 🎓 Orientació sobre:
  - Itineraris formatius
  - Cicles formatius
  - Centres educatius
  - Sortides laborals
- 🔎 **Sistema avançat de cerca i filtres** de centres FP.
- 🗺️ Visualització de dades de centres (ubicació, web, oferta educativa).

---

## 🧩 Arquitectura del Sistema

Arquitectura desacoblada basada en API REST:

```
Usuari
  ↓
Frontend (Flet - Python)
  ↓
Backend API (Node.js + Express)
  ↓
IA & Dades (Amazon Bedrock · MySQL · Google GenAI)
```

🔐 Tota la comunicació es realitza exclusivament mitjançant el backend per garantir la seguretat i integritat de les dades.

---

## 🛠️ Tecnologies Utilitzades

| Capa | Tecnologia | Descripció |
|------|------------|------------|
| Frontend | Flet (Python) | Interfície multiplataforma |
| Backend | Node.js + Express | API REST |
| Base de dades | MySQL | Dades estructurades FP |
| IA | Amazon Bedrock | Agents intel·ligents |
| Emmagatzematge | Amazon S3 | Documents oficials |

---

## ⚙️ Metodologia de Desenvolupament

Metodologia **Àgil basada en Scrum**:

- 🕒 Sprints de 2 setmanes
- ⚡ Prototipat ràpid
- 🔁 Disseny iteratiu d'agents IA
- 🌱 Control de versions amb Git i GitHub

---

## 🤖 Intel·ligència Artificial

### Model seleccionat
- **Nova Pro 1.0**

### Criteris de selecció
- ✅ Precisió en continguts normatius
- ⚡ Velocitat de resposta
- 💰 Cost sostenible

### Agent IA
- **FP-Agent-01**
- Configurat com a assistent especialitzat en Formació Professional valenciana

---

## 🗂️ Gestió de Dades

### Fonts d'informació
Totes les dades provenen **exclusivament de fonts oficials de la Generalitat Valenciana**:

- Catàlegs de FP (grau bàsic, mitjà i superior)
- Proves d'accés
- Currículums i mòduls
- Cursos d'especialització

### Garantia de veracitat
- Font única oficial
- Traçabilitat completa
- Validació manual inicial
- Exclusió de generació inventada

---

## 🎨 Experiència d'Usuari (UX/UI)

- 💡 Interfície clara i intuïtiva
- 📱 Multiplataforma (web i mòbil)
- ♿ Accessibilitat:
  - Alt contrast
  - Compatibilitat amb lectors de pantalla
  - Navegació per teclat

---

## 🔍 Cerca Avançada de Centres

Filtres disponibles:

- Província (Castelló, València, Alacant)
- Comarca
- Localitat
- Família professional
- Grau (Bàsic, Mitjà, Superior)
- Cicles

Cada centre mostra:
- 📍 Ubicació
- 🌐 Web oficial
- 🎓 Oferta educativa

---

## 🚀 Futur del Projecte

Pròximes millores previstes:

- ➕ Integració de FP Dual
- 🎙️ Conversió veu ↔ text
- 🤝 Agents especialitzats
- 📈 Ampliació de fonts de dades

---

## 📜 Llicència

Projecte educatiu i demostratiu.

---

## ⭐ Valor del Projecte

Aquest sistema representa un **avenç significatiu en la digitalització de l'orientació acadèmica**, millorant l'eficiència dels orientadors i oferint informació fiable a tota la comunitat educativa.

---

