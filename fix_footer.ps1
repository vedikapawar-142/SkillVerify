
$ErrorActionPreference = "Stop"

# Project root se run karo
$path = ".\app\templates\base.html"

if (-not (Test-Path -LiteralPath $path)) {
    Write-Host "ERROR: base.html not found!" -ForegroundColor Red
    exit 1
}

$content = Get-Content -LiteralPath $path -Raw

# Purane footer ko identify karo
$pattern = '(?s)<footer\b[^>]*class\s*=\s*["''](?=[^"'']*\bpy-4\b)(?=[^"'']*\bmt-auto\b)(?=[^"'']*\bborder-top\b)(?=[^"'']*\bbg-white\b)[^"'']*["''][^>]*>.*?</footer>'

$newFooter = @'
<footer class="site-footer">
    <div class="footer-gradient"></div>

    <div class="container footer-content">
        <div class="row g-4">
            <div class="col-6 col-md-3">
                <h6>For Candidates</h6>
                <a href="{{ url_for('auth.register') }}">Create an Account</a>
                <a href="{{ url_for('auth.login') }}">Candidate Login</a>
                <a href="{{ url_for('auth.login') }}">Skill Assessment</a>
            </div>

            <div class="col-6 col-md-3">
                <h6>For Recruiters</h6>
                <a href="{{ url_for('auth.hr_login') }}">HR Login</a>
                <a href="{{ url_for('auth.hr_login') }}">Candidate Evaluation</a>
                <a href="{{ url_for('auth.hr_login') }}">Assessment Reports</a>
            </div>

            <div class="col-6 col-md-3">
                <h6>Support &amp; Policies</h6>
                <a href="mailto:support@example.com">Help &amp; Support</a>
                <a href="#privacy-policy">Privacy Policy</a>
                <a href="#terms">Terms &amp; Conditions</a>
            </div>

            <div class="col-6 col-md-3">
                <h6>About SkillVerify</h6>
                <a href="{{ url_for('main.index') }}">About the Platform</a>
                <a href="mailto:support@example.com">Contact Us</a>
            </div>
        </div>

        <div class="footer-bottom">
            <span>&copy; 2026 AI Skill Verification Platform. All rights reserved.</span>
            <nav aria-label="Legal links">
                <a href="#privacy-policy">Privacy</a>
                <span class="footer-separator">/</span>
                <a href="#terms">Terms of Use</a>
                <span class="footer-separator">/</span>
                <a href="mailto:support@example.com">Contact</a>
            </nav>
        </div>
    </div>
</footer>
'@

if ($content -match $pattern) {
    # Backup before changing HTML
    $backupPath = "$path.bak"
    Copy-Item -LiteralPath $path -Destination $backupPath -Force

    $updatedContent = [regex]::Replace(
        $content,
        $pattern,
        [System.Text.RegularExpressions.MatchEvaluator]{
            param($match)
            return $newFooter
        },
        1
    )

    Set-Content -LiteralPath $path -Value $updatedContent -Encoding utf8

    Write-Host "SUCCESS: Footer replaced!" -ForegroundColor Green
    Write-Host "Backup: $backupPath" -ForegroundColor Cyan
}
else {
    Write-Host "ERROR: Old footer not found." -ForegroundColor Red
    Write-Host "No changes made. Check the footer classes in base.html." -ForegroundColor Yellow
}
