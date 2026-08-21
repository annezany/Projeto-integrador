const eye = document.querySelector('#leftEye');
const iris = eye.querySelector('.iris');

function moveIris(event) {
  const eyeBounds = eye.getBoundingClientRect();
  const eyeCenterX = eyeBounds.left + eyeBounds.width / 2;
  const eyeCenterY = eyeBounds.top + eyeBounds.height / 2;
  const angle = Math.atan2(event.clientY - eyeCenterY, event.clientX - eyeCenterX);
  const distance = Math.min(eyeBounds.width * 0.17, Math.hypot(
    event.clientX - eyeCenterX,
    event.clientY - eyeCenterY
  ) * 0.17);

  const x = Math.cos(angle) * distance;
  const y = Math.sin(angle) * distance;
  iris.style.transform = `translate(${x}px, ${y}px)`;
}

document.addEventListener('pointermove', moveIris, { passive: true });
