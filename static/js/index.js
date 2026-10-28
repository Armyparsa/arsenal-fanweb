alert("dnisfheoc");

const matchData = document.getElementById("match-data");

if (matchData) {
  const matchDataText = matchData.dataset.matchData;

  if (matchDataText) {
    const matchData = new Date(matchDataText.replace(" ", "T"));
    console.log("Match date text:", matchDataText);
    console.log("Parsed match date:", matchData);
    console.log("Current date:", new Date());
    alert("Match date: " + matchDataText + "\nParsed date: " + matchData);

    const daysElement = document.getElementById("days");
    const hoursElement = document.getElementById("hours");
    const minutesElement = document.getElementById("minutes");
    const secondsElement = document.getElementById("seconds");

    function updateCountdown() {
      const difference = matchData - new Date();

      if (difference <= 0) {
        daysElement.textContent = "00";
        hoursElement.textContent = "00";
        minutesElement.textContent = "00";
        secondsElement.textContent = "00";
        return;
      }

      const days = Math.floor(difference / (1000 * 60 * 60 * 24));

      const hours = Math.floor((difference / (1000 * 60 * 60)) % 24);

      const minutes = Math.floor((difference / (1000 * 60)) % 60);

      const seconds = Math.floor((difference / 1000) % 60);

      daysElement.textContent = String(days).padStart(2, "0");
      hoursElement.textContent = String(hours).padStart(2, "0");
      minutesElement.textContent = String(minutes).padStart(2, "0");
      secondsElement.textContent = String(seconds).padStart(2, "0");
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
  }
}
