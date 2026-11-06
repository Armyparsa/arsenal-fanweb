const lineupData = document.getElementById("lineup-data");

if (lineupData) {
  const formations = JSON.parse(lineupData.dataset.formations);
  const players = JSON.parse(lineupData.dataset.players);
  const savedPlayers = JSON.parse(lineupData.dataset.savedPlayers || "[]");

  const formationSelect = document.getElementById("formation-select");
  const pitchSlots = document.getElementById("pitch-slots");

  const selectPlayers = {};

  function showPlayer(playerSlot, player) {
    playerSlot.innerHTML = "";

    const shirt = document.createElement("span");
    shirt.className = "player-shirt";
    shirt.textContent = "*";

    const name = document.createElement("span");
    name.className = "player-name";
    name.textContent = player.name;

    playerSlot.append(shirt, name);
  }

  const formationPositions = {
    "4-3-3": {
      GK: [50, 90],
      LB: [15, 70],
      CB1: [38, 70],
      CB2: [62, 70],
      RB: [85, 70],
      CM1: [25, 45],
      CM2: [50, 45],
      CM3: [75, 45],
      LW: [20, 20],
      ST: [50, 12],
      RW: [80, 20],
    },

    "4-4-2": {
      GK: [50, 90],
      LB: [15, 70],
      CB1: [38, 70],
      CB2: [62, 70],
      RB: [85, 70],
      LM: [15, 45],
      CM1: [40, 45],
      CM2: [60, 45],
      RM: [85, 45],
      ST1: [38, 18],
      ST2: [62, 18],
    },

    "4-2-3-1": {
      GK: [50, 90],
      LB: [15, 70],
      CB1: [38, 70],
      CB2: [62, 70],
      RB: [85, 70],
      DM1: [38, 53],
      DM2: [62, 53],
      LAM: [20, 32],
      CAM: [50, 32],
      RAM: [80, 32],
      ST: [50, 12],
    },

    "4-3-1-2": {
      GK: [50, 90],
      LB: [15, 70],
      CB1: [38, 70],
      CB2: [62, 70],
      RB: [85, 70],
      CM1: [25, 50],
      CM2: [50, 50],
      CM3: [75, 50],
      CAM: [50, 30],
      ST1: [38, 12],
      ST2: [62, 12],
    },

    "4-1-4-1": {
      GK: [50, 90],
      LB: [15, 70],
      CB1: [38, 70],
      CB2: [62, 70],
      RB: [85, 70],
      DM: [50, 57],
      LM: [15, 35],
      CM1: [38, 35],
      CM2: [62, 35],
      RM: [85, 35],
      ST: [50, 12],
    },

    "4-2-2-2": {
      GK: [50, 90],
      LB: [15, 70],
      CB1: [38, 70],
      CB2: [62, 70],
      RB: [85, 70],
      DM1: [38, 55],
      DM2: [62, 55],
      LAM: [30, 32],
      RAM: [70, 32],
      ST1: [38, 12],
      ST2: [62, 12],
    },

    "3-4-3": {
      GK: [50, 90],
      CB1: [25, 70],
      CB2: [50, 70],
      CB3: [75, 70],
      LM: [12, 45],
      CM1: [38, 45],
      CM2: [62, 45],
      RM: [88, 45],
      LW: [20, 18],
      ST: [50, 12],
      RW: [80, 18],
    },

    "3-5-2": {
      GK: [50, 90],
      CB1: [25, 70],
      CB2: [50, 70],
      CB3: [75, 70],
      LM: [10, 48],
      CM1: [30, 45],
      CM2: [50, 48],
      CM3: [70, 45],
      RM: [90, 48],
      ST1: [38, 15],
      ST2: [62, 15],
    },

    "3-4-2-1": {
      GK: [50, 90],
      CB1: [25, 70],
      CB2: [50, 70],
      CB3: [75, 70],
      LM: [12, 48],
      CM1: [38, 48],
      CM2: [62, 48],
      RM: [88, 48],
      AM1: [35, 28],
      AM2: [65, 28],
      ST: [50, 10],
    },

    "5-3-2": {
      GK: [50, 90],
      LWB: [10, 68],
      CB1: [30, 70],
      CB2: [50, 70],
      CB3: [70, 70],
      RWB: [90, 68],
      CM1: [25, 45],
      CM2: [50, 45],
      CM3: [75, 45],
      ST1: [38, 15],
      ST2: [62, 15],
    },
  };

  function renderFormation() {
    const formation = formations[formationSelect.value];
    const positions = formationPositions[formationSelect.value];

    pitchSlots.innerHTML = "";

    formation.forEach(([slot, playerPosition]) => {
      const playerSlot = document.createElement("button");

      playerSlot.type = "button";
      playerSlot.className = "player-slot";
      playerSlot.dataset.slot = slot;
      playerSlot.dataset.position = playerPosition;

      const [x, y] = positions[slot];

      playerSlot.style.left = `${x}%`;
      playerSlot.style.top = `${y}%`;

      const savedPlayer = savedPlayers.find((player) => player.slot === slot);

      if (savedPlayer) {
        const player = players.find(
          (player) => player.id === savedPlayer.player_id,
        );

        if (player) {
          selectPlayers[slot] = player.id;
          showPlayer(playerSlot, player);
        } else {
          playerSlot.innerHTML = `
              <span class="player-shirt">+</span>
              <span class="slot-label">${slot}</span>
            `;
        }
      } else {
        playerSlot.innerHTML = `
            <span class="player-shirt">+</span>
            <span class="slot-label">${slot}</span>
          `;
      }

      playerSlot.addEventListener("click", () => {
        choosePlayer(playerSlot, slot, playerPosition);
      });

      pitchSlots.appendChild(playerSlot);
    });
  }

  const playerPicker = document.getElementById("player-picker");
  const pickerPlayers = document.getElementById("picker-players");
  const pickerTitle = document.querySelector(".picker-title");
  const closePicker = document.getElementById("close-picker");

  function choosePlayer(playerSlot, slot, position) {
    pickerTitle.textContent = `Choose ${position}`;

    pickerPlayers.innerHTML = "";

    const availablePlayers = players.filter((player) => {
      if (player.positions !== position) {
        return false;
      }

      return !Object.entries(selectPlayers).some(
        ([selectedSlot, selectedPlayerId]) =>
          selectedSlot !== slot && selectedPlayerId === player.id,
      );
    });

    availablePlayers.forEach((player) => {
      const playerButton = document.createElement("button");

      playerButton.type = "button";
      playerButton.className = "picker-player";

      const number = document.createElement("span");
      number.textContent = `#${player.shirt_number}`;

      const name = document.createElement("span");
      name.textContent = player.name;

      playerButton.append(number, name);

      playerButton.addEventListener("click", () => {
        selectPlayers[slot] = player.id;

        showPlayer(playerSlot, player);

        playerPicker.hidden = true;
      });

      pickerPlayers.appendChild(playerButton);
    });

    playerPicker.hidden = false;
  }

  closePicker.addEventListener("click", () => {
    playerPicker.hidden = true;
  });

  formationSelect.addEventListener("change", () => {
    Object.keys(selectPlayers).forEach((key) => {
      delete selectPlayers[key];
    });

    savedPlayers.length = 0;

    renderFormation();
  });

  renderFormation();

  const saveButton = document.getElementById("save-lineup");

  saveButton.addEventListener("click", async () => {
    const formation = formationSelect.value;

    if (Object.keys(selectPlayers).length !== 11) {
      alert("Please select 11 players before saving.");
      return;
    }

    const response = await fetch("/save-lineup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        formation: formation,
        players: selectPlayers,
      }),
    });

    const result = await response.json();

    if (result.success) {
      alert("Line-up saved successfully!");
    } else {
      alert(result.message || "Could not save line-up");
    }
  });
}
