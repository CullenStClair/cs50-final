function makeform()
{
    let num = parseInt(document.querySelector('#num').value, 10);
    let traits = document.querySelector('#traits').value.split(',');
    document.querySelector('#buh').innerHTML = '';
    for (i = 0; i < num; i++)
    {
        document.querySelector("#buh").innerHTML += `<select id="s${i}"></select>`;
        for (n = 0; n < traits.length; n++)
        {
            document.querySelector("#s"+i).innerHTML += `<option>${traits[n]}</option>`;
        }
    }
    return false;
}