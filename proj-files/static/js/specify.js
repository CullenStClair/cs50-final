function makeform()
{
    // retrieve data
    window.numb = parseInt(document.querySelector('#combnum').value, 10);
    let traits = document.querySelector('#traits').value.split(',');
    // validate user input
    if (numb > traits.length / 2 || numb < 2 || isNaN(numb))
    {
        document.querySelector("#buh").innerHTML = `
            <span class="lead">Invalid number. Min: 2 Max: ${traits.length / 2}</span>`;
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
    let session = document.querySelector("#session").value;
    // collect chosen traits, check if there is any repeats
    for (i = 0; i < window.numb; i++)
    {
        select = document.getElementById(`s${i}`);
        selected = select.selectedIndex;
        option = select.options[selected];
        if (traits.includes(option.value))
        {
            document.querySelector("#return").innerHTML = `<hr><span class="lead">Traits cannot be repeated.</span>`;
            return false;
        }
        traits[i] = option.value;
    }
    traits = traits.toString();
    req = {
        traits: traits,
        session: session
    };
    dat = Object.create(req);
    // request probability from server via AJAX (jQuery)
    let url = "http://localhost:5000/specify/prob";
    $.ajax({
        method: 'GET',
        url: url,
        async: false,
        dataType: 'json',
        data: dat,
        timeout: 60000,
        success: (data, textStatus, jqXHR) => {
            console.log(data)
            window.totalchance = 100 * parseFloat(data['data'], 10)
            // show probability as a percent
            document.querySelector("#return").innerHTML = `<hr><span class="lead">The chance of these traits showing together is:<br>${(window.totalchance).toFixed(2)}%</span>`;
        }
    });
    return false;
}