#import <Cocoa/Cocoa.h>

static NSString *run(NSString *binary, NSArray *args, int *code) {
    NSTask *task = [[NSTask alloc] init];
    task.executableURL = [NSURL fileURLWithPath:binary];
    task.arguments = args;
    NSPipe *pipe = [NSPipe pipe];
    task.standardOutput = pipe;
    task.standardError = pipe;
    NSError *err = nil;
    if (![task launchAndReturnError:&err]) { *code = 1; return err.localizedDescription; }
    NSData *data = [pipe.fileHandleForReading readDataToEndOfFile];
    [task waitUntilExit];
    *code = task.terminationStatus;
    NSString *s = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    return [(s ?: @"") stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceAndNewlineCharacterSet];
}

static NSString *python(void) {
    // macOS may expose /usr/bin/python3 as a developer-tools installation stub.
    // Probe only already-installed executables. Never call the stub or xcrun to fetch tools.
    NSMutableArray *candidates = [NSMutableArray arrayWithArray:@[
        @"/opt/homebrew/bin/python3", @"/usr/local/bin/python3",
        @"/Library/Frameworks/Python.framework/Versions/Current/bin/python3"]];
    int rc;
    NSString *developer = run(@"/usr/bin/xcode-select", @[@"-p"], &rc);
    if (rc == 0) [candidates addObject:[developer stringByAppendingPathComponent:@"usr/bin/python3"]];
    for (NSString *path in candidates) {
        if (![NSFileManager.defaultManager isExecutableFileAtPath:path]) continue;
        run(path, @[@"-I", @"-B", @"-c", @"import sys;sys.exit(sys.version_info[:2] < (3, 8))"], &rc);
        if (rc == 0) return path;
    }
    return nil;
}

static NSInteger dialog(NSString *title, NSString *text, NSArray *buttons) {
    NSAlert *a = [NSAlert new];
    a.messageText = title;
    a.informativeText = text;
    for (NSString *label in buttons) [a addButtonWithTitle:label];
    a.buttons.firstObject.keyEquivalent = @"\r";
    return [a runModal] - NSAlertFirstButtonReturn;
}

int main(int argc, const char **argv) {
    @autoreleasepool {
        NSString *script = [NSBundle.mainBundle.resourcePath stringByAppendingPathComponent:@"install_team.py"];
        NSString *py = python();
        int rc = 0;
        if (argc == 3 && strcmp(argv[1], "--test-preview") == 0) {
            if (!py) return 2;
            NSString *s = run(py, @[@"-I", @"-B", script, @"preview", @"--test-root",
                                   [NSString stringWithUTF8String:argv[2]]], &rc);
            puts(s.UTF8String);
            return rc;
        }
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp activateIgnoringOtherApps:YES];
        NSString *intro = @"一人成阵 · 三席交付　0.1.0\n首席接单，生产官制件，审核官检查同一版本。\n\n安装只登记本机私有专家。运行任务时 WorkBuddy 按账户规则计费。";
        if (!py) {
            dialog(@"可以预览，本机暂未找到 Python 3.8 或以上版本",
                   [intro stringByAppendingString:@"\n\nWorkBuddy 5.9.3 的官方注册脚本需要已有的 Python。本工具已停在预览。你也可以在客户端「我的专家 → 创建专家团」走官方创建流程；该流程对这个冻结包的等价导入尚未验证。"], @[@"关闭"]);
            return 0;
        }
        NSString *status = run(py, @[@"-I", @"-B", script, @"preview"], &rc);
        if (rc) { dialog(@"当前条件无法安装", status, @[@"关闭"]); return 1; }
        NSString *combined = [NSString stringWithFormat:@"%@\n\n%@\n\n写入前请自行退出 WorkBuddy，并保存当前任务。", intro, status];
        NSMutableArray *buttons = [NSMutableArray arrayWithObject:@"关闭"];
        NSMutableArray *actions = [NSMutableArray arrayWithObject:@""];
        if ([status hasPrefix:@"可以安装"] || [status hasPrefix:@"上次安装"]) {
            [buttons addObject:@"登记本团"]; [actions addObject:@"install"];
        }
        if ([status hasPrefix:@"本工具已安装"] || [status hasPrefix:@"上次安装"]) {
            [buttons addObject:@"撤回本次新增"]; [actions addObject:@"undo"];
        }
        NSInteger pick = dialog(@"一人成阵 · 安装预览", combined, buttons);
        if (pick <= 0 || pick >= (NSInteger)actions.count) return 0;
        NSString *action = actions[pick];
        BOOL install = [action isEqualToString:@"install"];
        NSString *confirm = install
          ? @"将把已核对的十个文件写入本机 WorkBuddy 专家目录，并增加一条登记。之后可重新打开此工具撤回。"
          : @"将移除本工具新增的那一条登记，把本次写入的原文件移到本机撤回留存区。若内容已改动，将保留现状。";
        if (dialog(install ? @"登记这支专家团？" : @"撤回本工具新增的团队？",
                   confirm, @[@"取消", install ? @"确认登记" : @"确认撤回"]) != 1) return 0;
        NSString *result = run(py, @[@"-I", @"-B", script, action], &rc);
        dialog(rc ? @"操作未完成" : @"操作结果", result, @[@"关闭"]);
        return rc;
    }
}

