document.addEventListener('DOMContentLoaded', function () {

    const colorMapping = {
        'z': '#34ff20',
        'v': '#01ffea',
        'russian_flag': '#ff0000',
        'colorado': '#2200ff'
    }

    for (const elem of document.getElementsByClassName('annotated-image')) {
        var anno = Annotorious.init({
            image: elem, // image element or ID,
            readOnly: true,
            formatter: function (annotation) {
                return {
                    'style': `stroke-width:2; stroke: ${colorMapping[annotation.body[0].label]}`
                }

            }
        });
        const annotations = JSON.parse(elem.dataset.annotations)
        for (const an of annotations) {
            anno.addAnnotation(an);
        }
    }
})