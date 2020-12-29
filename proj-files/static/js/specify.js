function makeform()
{
    // retrieve data
    window.numb = parseInt(document.querySelector('#combnum').value, 10);
    let traits = document.querySelector('#traits').value.split(',');
    // validate user input
    if (numb > traits.length || numb < 2 || isNaN(numb))
    {
        document.querySelector("#buh").innerHTML = `
            <span class="lead">Invalid number. Min: 2 Max: ${traits.length}</span>`;
        return false
    }
    // generate form
    content = `
        <hr>
        <form class="form" onsubmit='calculate();return false;'>`;
    // generate <select> elements
    for (i = 0; i < numb; i++)
    {
        content += `
            <span class="lead">Trait ${i + 1}:</span>
            <div style="margin-bottom:2%;">
            <select id="s${i}">`;
        // generate <option> elements
        for (n = 0; n < traits.length; n++)
        {
            // auto-select first option
            if (n == 0)
            {
                content += `
                <option selected value="${traits[n]}">${traits[n]}</option>`;
            }
            else
            {
                content += `
                <option value="${traits[n]}">${traits[n]}</option>`;
            }
        }
        content += `</select></div>`;
    }
    // generate closing html
    content += `
        <button type="submit" class="btn btn-primary">Calculate</button></form>`;
    // output content
    document.querySelector("#buh").innerHTML = content;
    return false;
}

function calculate()
{
    let traits = Array(window.numb).fill("");
    // collect chosen traits
    for (i = 0; i < window.numb; i++)
    {
        select = document.getElementById(`s${i}`);
        selected = select.selectedIndex;
        option = select.options[selected];
        traits[i] = option.value;
    }
    traits = traits.toString();
    // request probability from server via AJAX/getJSON (jQuery)
    let url = "http://127.0.0.1:5000/specify/prob";
    $.getJSON(url, traits, function(data, textStatus, jqXHR){
        alert(data);
    });
    return false;
}