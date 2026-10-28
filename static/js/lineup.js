const lineupData = document.getElementById("lineup-data");

if (lineupData) {
  const formations = JSON.parse(lineupData.dataset.formations);
  const players = JSON.parse(lineupData.dataset.players);
  const savedPlayers = JSON.parse(lineupData.dataset.savedPlayers || "[]");

  const formationSelect = document.getElementById("formation-select");
  const pitchSlots = document.getElementById("pitch-slots");

  const selectPlayers = {};

  function renderFormation() {
    const formation = formations[formationSelect.value];

    pitchSlots.innerHTML = "";

    formation.forEach(([slot, position]) => {
      const playerSlot = document.createElement("button");

      playerSlot.type = "button";
      playerSlot.className = "player-slot";
      playerSlot.dataset.slot = slot;
      playerSlot.dataset.position = position;

      const savedPlayer = savedPlayers.find((player) => player.slot === slot);

      if (savedPlayer) {
        const player = players.find(
          (player) => player.id === savedPlayer.player_id,
        );

        if (player) {
          selectPlayers[slot] = player.id;

          playerSlot.innerHTML = `
        <span class="player-shirt">*</span>
        <span class="player-name">${player.name}</span>
      `;
        }
      } else {
        playerSlot.innerHTML = `
        <span class="player-shirt">+</span>
        <span class="slot-label">${slot}</span>
      `;
      }

      playerSlot.addEventListener("click", () => {
        choosePlayer(playerSlot, slot, position);
      });

      pitchSlots.appendChild(playerSlot);
    });
  }

  function choosePlayer(playerSlot, slot, position) {
    const currentPlayer = selectPlayers[slot];

    const availablePlayers = players.filter((player) => {
      if (player.positions !== position) {
        return false;
      }

      const selectedElsewhere = Object.entries(selectPlayers).some(
        ([selectedSlot, selectedPlayerId]) => {
          return selectedSlot !== slot && selectedPlayerId === player.id;
        },
      );

      return !selectedElsewhere;
    });

    if (availablePlayers.length === 0) {
      alert("No available players for this position.");
      return;
    }

    let message = "Choose a player:\n\n";

    availablePlayers.forEach((player, index) => {
      message += `${index + 1}. ${player.name} (#${player.shirt_number})\n`;
    });

    const choice = prompt(message);

    if (choice === null) {
      return;
    }

    const index = parseInt(choice) - 1;

    if (Number.isNaN(index) || index < 0 || index >= availablePlayers.length) {
      alert("Invalid player selection.");
      return;
    }

    const player = availablePlayers[index];

    selectPlayers[slot] = player.id;

    playerSlot.innerHTML = `
    <span class="player-shirt">*</span>
    <span class="player-name">${player.name}</span>
    `;
  }

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
