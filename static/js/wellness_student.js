document.querySelectorAll('nav a:not([href="/back_to_student"])').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default link behavior (page reload or navigation)

        const targetId = this.getAttribute('href').substring(1); // Get the target ID from href attribute
        const targetElement = document.getElementById(targetId); // Find the target element by ID

        if (targetElement) {
            const headerHeight = document.querySelector('header').offsetHeight; // Get height of header

            // Scroll to the target element with smooth behavior
            window.scrollTo({
                top: targetElement.offsetTop - headerHeight, // Calculate scroll position relative to header
                behavior: 'smooth' // Smooth scrolling animation
            });
        }
    });
});


document.getElementById('exercise-button').addEventListener('click', function() {
    const exercises = [
        'Take a 5-minute mindful breathing break.',
        'Write down 3 things you are grateful for.',
        'Stretch your body for 5 minutes.',
        'Take a short walk and observe your surroundings.',
        'Listen to a calming piece of music.',
        'Do a quick 5-minute meditation.',
        'Draw or doodle something for 5 minutes.',
        'Spend 5 minutes organizing your study space.',
        'Practice a quick yoga routine.',
        'Read a motivational quote and reflect on it.',
        'Drink a glass of water and stay hydrated.',
        'Write a positive affirmation and say it out loud.',
        'Do a quick 5-minute workout or dance.',
        'Visualize a peaceful place and stay there for a few minutes.',
        'Take a moment to focus on your breathing, counting each inhale and exhale.',
        'Practice a relaxation technique like progressive muscle relaxation.',
        'Spend a few minutes petting your pet or looking at pictures of animals.',
        'Close your eyes and imagine a favorite happy memory.',
        'Write a short, positive message to a friend or family member.',
        'Do a simple puzzle or brain game to shift your focus.'
    ];

    const exerciseOutput = document.getElementById('exercise-output');
    const randomExercise = exercises[Math.floor(Math.random() * exercises.length)];
    exerciseOutput.textContent = randomExercise;
});

document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();
    alert('Thank you for your message!');
});