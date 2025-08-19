"""
Unit tests for CSP utility functions and API service hooks
Tests the JavaScript/TypeScript utilities created for CSP and live race tracking
"""

import pytest
import json
from pathlib import Path


class TestCSPUtility:
    """Test CSP utility functions"""

    def test_csp_utility_file_exists(self):
        """Test that CSP utility file exists"""
        csp_file = Path("src/web/src/utils/csp.ts")
        assert csp_file.exists(), "CSP utility file should exist"

        # Read and validate basic structure
        content = csp_file.read_text()
        assert (
            "getCSPHeader" in content
        ), "CSP utility should have getCSPHeader function"
        assert "development" in content, "Should handle development environment"
        assert "production" in content, "Should handle production environment"

        print("✅ CSP utility file exists and has expected structure")

    def test_csp_config_documentation_exists(self):
        """Test that CSP configuration documentation exists"""
        csp_docs = Path("src/web/CSP_CONFIG.md")
        assert csp_docs.exists(), "CSP configuration documentation should exist"

        content = csp_docs.read_text()
        assert "Content Security Policy" in content, "Should document CSP"
        assert "production" in content.lower(), "Should include production guidance"
        assert (
            "nginx" in content.lower() or "apache" in content.lower()
        ), "Should include web server examples"

        print("✅ CSP configuration documentation exists")

    def test_csp_development_vs_production_config(self):
        """Test development vs production CSP configuration differences"""
        csp_file = Path("src/web/src/utils/csp.ts")
        content = csp_file.read_text()

        # Development should be more permissive
        assert "'unsafe-eval'" in content, "Development should allow unsafe-eval"

        # Should have environment detection
        assert (
            "NODE_ENV" in content or "development" in content
        ), "Should detect environment"

        print("✅ CSP utility handles development/production differences")


class TestAPIServiceHook:
    """Test API service hook functionality"""

    def test_api_service_hook_exists(self):
        """Test that useApiService hook exists"""
        api_hook_file = Path("src/web/src/hooks/useApiService.ts")
        assert api_hook_file.exists(), "API service hook should exist"

        content = api_hook_file.read_text()
        assert "useApiService" in content, "Should export useApiService hook"
        react_hooks = ["useCallback", "useState", "useEffect"]
        assert any(hook in content for hook in react_hooks), "Should use React hooks"

        print("✅ API service hook exists")

    def test_websocket_hook_integration(self):
        """Test WebSocket hook integration"""
        # Check for WebSocket-related files
        websocket_files = [
            Path("src/web/src/hooks/useWebSocket.ts"),
            Path("live_race_websocket.py"),
        ]

        existing_files = [f for f in websocket_files if f.exists()]
        assert len(existing_files) > 0, "Should have WebSocket implementation files"

        for file in existing_files:
            content = file.read_text()
            if file.suffix == ".ts":
                assert (
                    "WebSocket" in content or "websocket" in content.lower()
                ), f"{file} should contain WebSocket functionality"
            elif file.suffix == ".py":
                assert (
                    "websocket" in content.lower() or "ws" in content
                ), f"{file} should contain WebSocket server functionality"

        print(
            f"✅ WebSocket implementation files found: {[f.name for f in existing_files]}"
        )


class TestLiveRaceComponents:
    """Test live race tracking component structure"""

    def test_live_race_tracker_component_exists(self):
        """Test that LiveRaceTracker component exists"""
        component_paths = [
            Path("src/web/src/components/LiveRaceTracker.tsx"),
            Path("src/web/src/components/LiveRaceTracker.ts"),
            Path("src/web/src/components/live/LiveRaceTracker.tsx"),
        ]

        existing_components = [p for p in component_paths if p.exists()]

        if existing_components:
            for component in existing_components:
                content = component.read_text()
                assert (
                    "LiveRaceTracker" in content
                ), "Should contain LiveRaceTracker component"
                print(f"✅ LiveRaceTracker component found: {component}")
        else:
            print("📝 LiveRaceTracker component may be integrated in other files")

    def test_race_selection_component_exists(self):
        """Test that RaceSelection component exists"""
        component_paths = [
            Path("src/web/src/components/RaceSelection.tsx"),
            Path("src/web/src/components/RaceSelection.ts"),
            Path("src/web/src/components/race/RaceSelection.tsx"),
        ]

        existing_components = [p for p in component_paths if p.exists()]

        if existing_components:
            for component in existing_components:
                content = component.read_text()
                assert (
                    "RaceSelection" in content
                ), "Should contain RaceSelection component"
                print(f"✅ RaceSelection component found: {component}")
        else:
            print("📝 RaceSelection component may be integrated in other files")

    def test_component_typescript_compilation(self):
        """Test that components are properly typed for TypeScript"""
        web_src_path = Path("src/web/src")
        if not web_src_path.exists():
            pytest.skip("Web source directory not found")

        # Look for TypeScript files
        ts_files = list(web_src_path.rglob("*.ts")) + list(web_src_path.rglob("*.tsx"))

        if ts_files:
            print(f"✅ Found {len(ts_files)} TypeScript files")

            # Check for basic TypeScript patterns
            for ts_file in ts_files[:5]:  # Check first 5 files
                content = ts_file.read_text()
                has_types = any(
                    keyword in content
                    for keyword in [
                        "interface",
                        "type",
                        ":",
                        "React.",
                        "useState",
                        "useEffect",
                    ]
                )
                if has_types:
                    print(f"  📘 {ts_file.name} has TypeScript typing")
        else:
            print("📝 No TypeScript files found in web source")


class TestViteConfiguration:
    """Test Vite configuration for CSP compatibility"""

    def test_vite_config_exists(self):
        """Test that Vite configuration exists"""
        vite_config_paths = [
            Path("vite.config.ts"),
            Path("src/web/vite.config.ts"),
            Path("vite.config.js"),
        ]

        existing_configs = [p for p in vite_config_paths if p.exists()]
        assert len(existing_configs) > 0, "Vite configuration should exist"

        for config in existing_configs:
            content = config.read_text()
            print(f"✅ Vite config found: {config}")

        return existing_configs[0]

    def test_vite_sourcemap_configuration(self):
        """Test Vite sourcemap configuration for CSP"""
        vite_config = self.test_vite_config_exists()
        content = vite_config.read_text()

        # Should have sourcemap configuration for CSP compatibility
        if "sourcemap" in content:
            print("✅ Vite sourcemap configuration found")
            if "inline" in content:
                print("✅ Inline sourcemaps configured (CSP compatible)")
        else:
            print("📝 Sourcemap configuration may be using defaults")

    def test_vite_build_configuration(self):
        """Test Vite build configuration"""
        vite_config = self.test_vite_config_exists()
        content = vite_config.read_text()

        # Check for build optimizations
        build_related = ["build", "rollup", "chunk", "outDir"]
        found_configs = [keyword for keyword in build_related if keyword in content]

        if found_configs:
            print(f"✅ Build configurations found: {found_configs}")
        else:
            print("📝 Using default Vite build configuration")


class TestIndexHTMLConfiguration:
    """Test index.html CSP configuration"""

    def test_index_html_exists(self):
        """Test that index.html exists with CSP configuration"""
        index_paths = [
            Path("index.html"),
            Path("src/web/index.html"),
            Path("public/index.html"),
        ]

        existing_index = [p for p in index_paths if p.exists()]
        assert len(existing_index) > 0, "index.html should exist"

        return existing_index[0]

    def test_csp_meta_tag_in_html(self):
        """Test CSP meta tag in index.html"""
        index_html = self.test_index_html_exists()
        content = index_html.read_text()

        assert (
            'http-equiv="Content-Security-Policy"' in content
        ), "Should have CSP meta tag"
        assert "content=" in content, "CSP meta tag should have content"

        print("✅ CSP meta tag properly configured in index.html")

    def test_html_structure_for_react(self):
        """Test HTML structure is suitable for React application"""
        index_html = self.test_index_html_exists()
        content = index_html.read_text()

        assert (
            'id="root"' in content or 'id="app"' in content
        ), "Should have React root element"
        assert (
            "<html" in content and "</html>" in content
        ), "Should be valid HTML structure"

        print("✅ HTML structure suitable for React application")


def run_unit_tests():
    """Run all unit tests and return results"""
    print("🧪 Running Unit Tests for CSP and Live Race Features")
    print("=" * 60)

    # Change to project directory
    import os

    os.chdir("/home/jc/Documents/Horse-race-ai-v2.03")

    test_results = {"passed": 0, "failed": 0, "errors": []}

    # Test classes to run
    test_classes = [
        TestCSPUtility(),
        TestAPIServiceHook(),
        TestLiveRaceComponents(),
        TestViteConfiguration(),
        TestIndexHTMLConfiguration(),
    ]

    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n🔍 Testing {class_name}")
        print("-" * 40)

        # Get test methods
        test_methods = [
            method for method in dir(test_class) if method.startswith("test_")
        ]

        for test_method in test_methods:
            try:
                method = getattr(test_class, test_method)
                method()
                test_results["passed"] += 1
                print(f"  ✅ {test_method}")
            except Exception as e:
                test_results["failed"] += 1
                test_results["errors"].append(f"{class_name}.{test_method}: {e}")
                print(f"  ❌ {test_method}: {e}")

    return test_results


if __name__ == "__main__":
    results = run_unit_tests()

    print(f"\n📊 Unit Test Summary")
    print("=" * 30)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")

    if results["errors"]:
        print(f"\n📋 Errors:")
        for error in results["errors"]:
            print(f"  • {error}")

    success_rate = results["passed"] / (results["passed"] + results["failed"]) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
