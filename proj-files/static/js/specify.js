function makeform()
{
    alert("test1");
    let num = parseInt(document.querySelector("num").value);
    alert("test2")
    let traits = document.querySelector("traits").value;
    alert("test3");
    document.getElementById("buh").innerHTML = ``;
    for (i = 0; i < num; i++)
    {
        document.getElementById("buh").innerHTML += `<select id="s${i}"></select>`;
        for (n = 0; n < len(traits); n++)
        {
            document.getElementById("s"+i).innerHTML += `<option>${traits[n]}</option>`;
        }
    }
    return false;
}