from voivoi.cli import LOGO, run


def test_run_prints_logo(capsys):
    run()
    captured = capsys.readouterr()
    assert LOGO in captured.out
