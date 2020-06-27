/*
    A JS program too update the text on "/" when the 🔄 is clicked
*/
let i = 0;
let notes = [];
while (true) {
    if (document.getElementById(`note_${i}`) == null) {
        break;
    }
    notes.push(document.getElementById(`note_${i}`));
    i += 1;
}

console.log(notes);
notes[0].hidden = false;
i = 0;
function nextNote() {
    notes[i].hidden = true;
    console.log(i)
    if (i == (notes.length - 1)) {
        i = 0
    }
    else {
        i += 1;
    }
    notes[i].hidden = false;
}