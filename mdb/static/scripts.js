// 初始化Bootstrap的Tooltip
$(function() {
    $("[data-toggle='tooltip']").tooltip({container: "body", placement: "left"});
});

// 根据滚动显示或隐藏右上区按钮与回到顶部按钮
$(window).scroll(function() {
    if ($(window).scrollTop() >= 600) {
        $("#back_to_top_button").css("display", "inline-block").fadeIn();
        $(".top_right").fadeOut();
    } else {
        $("#back_to_top_button").fadeOut();
        $(".top_right").fadeIn();
    }
});

// 上传图片按钮行为
$(function() {
    $("#upload_button").click(function() {
        $("#upload_form input").click();
    });
    $("#upload_form input").change(function() {
        $("#upload_form").submit();
    });
});

// 登录表单验证
function validate_login_form() {
    $("#login_form small").remove();
    var username = $("#username");
    var password = $("#password")
    var label_username = $("label[for='username']")
    var label_password = $("label[for='password']")
    if (!username.val()) {
        label_username.append("<small class='warning'>* 必填</small>");
    }
    if (!password.val()) {
        label_password.append("<small class='warning'>* 必填</small>");
    }
    if (!username.val()) {
        username.focus();
        return false;
    } else if (!password.val()) {
        password.focus();
        return false;
    } else {
        return true;
    }
}
$(function() { $("#login_form").submit(validate_login_form); });

// 文章编辑表单验证
function validate_edit_form() {
    $("#edit_form small").remove();
    var title = $("#title");
    var label_title = $("label[for='title']");
    if (title.length && !title.val()) {
        label_title.append("<small class='warning'>* 必填</small>");
    }
    if (title.length && !title.val()) {
        title.focus();
        return false;
    } else {
        return true;
    }
}
$(function() { $("#edit_form").submit(validate_edit_form) });

// 显示一条自动淡出的消息
function show_message(message, type) {
    var msg = $("<div>", {class: "alert alert-" + type, html: "<b>" + message + "</b>"});
    msg.appendTo($(".messages")).delay(2000).fadeOut(3000);
};

// 异步提交文章编辑表单
function async_save(target) {
    $.ajax({
        url: target,
        type: "POST",
        data: $("#edit_form").serialize(),
        headers: {"Accept": "application/json"},
        beforeSend: validate_edit_form,
        success: function(data) {
            if (data.ok) {
                show_message("保存成功", "success");
            } else {
                show_message("保存失败", "danger");
            }
        },
    })
}

// 舍弃草稿并重置文章编辑表单
function clear_draft(url) {
    $("#confirm_modal").modal("hide");
    $("#edit_form input").val("")
    $("#edit_form textarea").html("")
    $.get(url, "", function() {show_message("草稿已舍弃", "success")});
}

// 动态内容加载器
var loader = {
    target: null,
    condition: {},
    loadable: true,
    load: function() {
        loader.loadable = false;
        $.ajax({
            url: loader.target,
            data: loader.condition,
            headers: {"Accept": "application/json"},
            success: function(data) {
                if (data["next"]) {
                    loader.condition.startswith = data["next"];
                    loader.loadable = true;
                }
                $("main").append(data["content"]);
            },
        });
    }
}
