const matchDataElement = document.getElementById("match-data");

if (matchDataElement) {
  const matchDataText = matchDataElement.dataset.matchData;

  const daysElement = document.getElementById("days");
  const hoursElement = document.getElementById("hours");
  const minutesElement = document.getElementById("minutes");
  const secondsElement = document.getElementById("seconds");

  if (
    matchDataText &&
    daysElement &&
    hoursElement &&
    minutesElement &&
    secondsElement
  ) {
    const matchData = new Date(matchDataText.replace(" ", "T"));

    const countdownInterval = setInterval(updateCountdown, 1000);

    function updateCountdown() {
      const difference = matchData - new Date();

      if (Number.isNaN(matchData.getTime()) || difference <= 0) {
        daysElement.textContent = "00";
        hoursElement.textContent = "00";
        minutesElement.textContent = "00";
        secondsElement.textContent = "00";
        clearInterval(countdownInterval);
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
  }
}
